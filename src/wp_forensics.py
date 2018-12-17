import os
import sys
import requests
import shutil
import tarfile
import glob
import re
import filecmp


class WpForensics:
    def __init__(self, version_info='', original_dir='', tmp_dir=None):
        if tmp_dir is None:
            self.tmp_dir = os.path.dirname(os.path.abspath(__file__)) + '/../tmp/'  # tmpディレクトリのパス
        else:
            self.tmp_dir = tmp_dir
        self.version_info = version_info  # バージョン名
        self.original_dir = original_dir  # WordPressの正規ファイルの場所
        self.lang = ''  # WPの言語設定

    def check_tmp(self):
        """
        WordPressなどを管理するtmpディレクトリを出す
        :return: 0: すでに存在する、 1: 存在しないので作成する
        """
        if os.path.isdir(self.tmp_dir):
            return 0
        else:
            os.mkdir(self.tmp_dir)
            return 1

    def check_wp(self, wp_dir):
        """
        WordPress のディレクトリかどうか確認する
        確認できたらバージョン情報を取得し、インスタンス変数に入れる
        :param wp_dir:
        :return: 0: WPのディレクトリ、 1-:たぶん違う
        """
        if os.path.isdir(wp_dir) is False:
            # ディレクトリが存在しない
            return 1
        version_file = wp_dir + '/wp-includes/version.php'
        if os.path.isfile(version_file) is False:
            # WPのディレクトリではない
            return 2
        version_get = False
        for line in open(version_file):
            if "$wp_version = " in line:
                version_get = True
                self.version_info = line.split("'")[1]
            if "$wp_local_package = " in line:
                self.lang = line.split('\'')[1]
        if version_get:
            return 0
        else:
            # バーション名の取得失敗
            return 3

    def download_wp(self):
        """
        requestsを使ってダウンロードまで
        :return: レスポンスデータ
        """
        if self.lang == 'ja':
            wp_url = "https://ja.wordpress.org/wordpress-" + self.version_info + "-ja.tar.gz"
        else:
            wp_url = "https://wordpress.org/wordpress-" + self.version_info + ".tar.gz"
        response_data = requests.get(wp_url, stream=True)
        return response_data

    def extract_wp(self, response_data):
        """
        レスポンスデータを tar ファイルに書き込んで展開する
        tar ファイルはその後消す
        :param response_data:
        :return:
        """
        tar_path = self.tmp_dir + 'download.tar.gz'
        with open(tar_path, "wb") as fp:
            shutil.copyfileobj(response_data.raw, fp)
        tar = tarfile.open(tar_path)
        tar.extractall(self.tmp_dir)
        tar.close()
        os.remove(tar_path)

    @staticmethod
    def get_file_list(wp_dir, wp_content_flag=True):
        """
        ファイルリスト一覧を取得する
        wp_dirは別途与えられるので、wp_dir を抜いた形で出力する
        :param wp_content_flag: Trueの場合 wp-content ディレクトリを無視する
        :param wp_dir:
        :return:
        """
        file_abs_list = glob.glob(wp_dir + "/**", recursive=True)
        file_list = []
        for file_abs_path in file_abs_list:
            if "wp-config.php" not in file_abs_path:
                if wp_content_flag:
                    if 'wp-content/' not in file_abs_path:
                        file_list.append(file_abs_path.replace(wp_dir + '/', ''))
                else:
                    file_list.append(file_abs_path.replace(wp_dir + '/', ''))
        return file_list

    def get_download_file(self, wp_file):
        """
        運用中のファイルパスからダウンロードしたファイルの絶対パスを指定する
        :param wp_file:
        :return:
        """
        abs_path = "%swordpress/%s" % (self.tmp_dir, wp_file)
        return abs_path

    @staticmethod
    def validate_wp_dir(wp_dir):
        """
        wp_dirが正しいかどうか検証する
        →いまの実装では「/」で終わってなければ修正するだけ
        :param wp_dir:
        :return:
        """
        wp_dir = re.sub(r'/$', "", wp_dir)
        return wp_dir

    def is_file_ok(self, wp_file):
        """
        wp_file がダウンロードした正規ファイルに存在するかどうか確認
        :param wp_file: 運用中のWPファイル
        :return: result:true の場合問題なし、False の場合問題あり
        """
        downloaded_target_file = "%swordpress/%s" % (self.tmp_dir, wp_file)
        file_result = {"result": None}
        if os.path.exists(downloaded_target_file):
            file_result["result"] = True
        else:
            file_result["result"] = False
        return file_result

    def is_file_modified(self, wp_dir, wp_file):
        """
        改ざんされていないかどうか確認
        is_file_ok が True の場合呼び出される
        :param wp_dir: WordPressの既存ファイルのディレクトリ
        :param wp_file: 対象ファイルの相対パス
        :return:
        """
        wp_target_file = "%s/%s" % (wp_dir, wp_file)
        downloaded_target_file = "%swordpress/%s" % (self.tmp_dir, wp_file)
        file_result = {"result": None}
        if os.path.isdir(wp_target_file):
            # ディレクトリの場合はOK
            file_result["result"] = True
        elif ".ttf" in wp_target_file or ".woff" in wp_target_file or ".eot" in wp_target_file:
            # フォントファイルは無視
            file_result["result"] = True
        elif ".gz" in wp_target_file:
            # 圧縮ファイルは無視
            file_result["result"] = True
        else:
            if filecmp.cmp(wp_target_file, downloaded_target_file):
                # diff 一致
                file_result["result"] = True
            else:
                file_result["result"] = False
        return file_result

    @staticmethod
    def is_file_binary(filename):
        # ディレクトリでない場合はスルー
        if os.path.isfile(filename) is False:
            return True
        # 画像かどうか確認する
        png_mn = bytearray([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        gif_mn = bytearray([0x47, 0x49, 0x46])
        jpeg_mn = bytearray([0xFF, 0xD8])
        header = bytearray()
        with open(filename, 'rb') as f:
            for i in range(0, 8):
                d = f.read(1)
                if len(d) > 0:  # ファイル内容が極端に短いときの対処
                    header.append(ord(d))
        if header == png_mn:
            # print("PNG")
            return True
        elif header[:3] == gif_mn:
            # print("GIF")
            return True
        elif header[:2] == jpeg_mn:
            # print("JPEG")
            return True
        else:
            return False

    def main(self, args):
        if len(args) is not 2:
            exit("argument error")
        wp_dir = self.validate_wp_dir(args[1])
        if self.check_wp(wp_dir) is False:
            exit("not WordPress Dir")
        print("WordPress is found : ver -> %s" % self.version_info)

        # 最初にtmpディレクトリがあるかどうか確認する、なければ追加
        self.check_tmp()

        # tmpディレクトリにダウンロード
        print("Download WordPress...")
        response_data = self.download_wp()
        print("Success")

        # ZIPを展開
        print("Extract WordPress...")
        self.extract_wp(response_data)

        # 現在のWPのファイルリストを取得
        wp_file_list = self.get_file_list(wp_dir)

        # 調査結果
        added_dict = []
        modified_dict = []
        binary_dict = []

        # 改ざん検知
        for file in wp_file_list:
            if self.is_file_ok(file)["result"]:
                # ファイルが存在するため、ファイルの改ざんをチェックする
                if self.is_file_modified(wp_dir, file)["result"]:
                    # ファイルが同一と判断された場合
                    pass
                else:
                    modified_dict.append(file)
            else:
                added_dict.append(file)

        # ディレクトリ検知
        wp_upload_dir = wp_dir + '/wp-content/uploads'
        upload_file_list = self.get_file_list(wp_upload_dir, False)
        for up_file in upload_file_list:
            target_file = "%s/%s" % (wp_upload_dir, up_file)
            is_file_binary = self.is_file_binary(target_file)
            if is_file_binary is False:
                binary_dict.append(up_file)

        # 結果
        print("\nAdded File(s)...")
        for add_item in added_dict:
            print(add_item)

        print("\nModifed File(s)...")
        for mod_item in modified_dict:
            print(mod_item)

        print("\nUnknown File(s)...")
        for bin_item in binary_dict:
            print(bin_item)

        print("\n\nDone.")


if __name__ == '__main__':
    WpForensics().main(sys.argv)

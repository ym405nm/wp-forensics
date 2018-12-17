from unittest import TestCase
from src.wp_forensics import WpForensics
import shutil
import os
import requests


class TestWpForensics(TestCase):

    def setUp(self):
        self.tmp_dir = './tmp/'
        # すでにディレクトリが存在すればテストをストップする（誤削除防止のため）
        if os.path.isdir(self.tmp_dir):
            self.fail("ディレクトリが既に存在します。./tmp ディレクトリを削除してください")
        self.wp = WpForensics(tmp_dir=self.tmp_dir)
        self.version_info = '4.9.8'  # テスト用のWPのバージョン
        # self.check_tmp = self.wp.check_tmp()
        # self.wp_dir = './assets/wordpress'  # テスト前にWordPressのファイルの準備が必要
        # self.check_wp = self.wp.check_wp(self.wp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_check_tmp(self):
        self.assertEqual(1, self.wp.check_tmp(), "tmpディレクトリの存在しないか")
        self.assertEqual(0, self.wp.check_tmp(), "tmpディレクトリが存在するか")

    def test_check_wp(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        download_dir = '%swordpress' % self.wp.tmp_dir
        os.mkdir("%sasset/" % self.wp.tmp_dir)
        asset_dir = '%sasset/wordpress' % self.wp.tmp_dir
        shutil.copytree(download_dir, asset_dir)
        self.wp.version_info = ''
        self.assertEqual(0, self.wp.check_wp(asset_dir), "既存のWPディレクトリが存在するか")
        self.assertEqual(
            self.version_info,
            self.wp.version_info,
            "バージョンの特定"
        )

    def test_download_wp(self):
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.assertEqual(
            requests.codes.ok,
            response_data.status_code,
            "正当にダウンロードされているか"
        )

    def test_extract_wp(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        self.assertTrue(
            os.path.isdir(self.tmp_dir + 'wordpress'),
            "ダウンロード後のファイルが存在するか")
        tar_path = self.tmp_dir + 'download.tar.gz'
        self.assertFalse(
            os.path.isfile(tar_path),
            "ダウンロードしたtarファイルは消せているか"
        )

    def test_validate_wp_dir(self):
        test_data = 'path/to/wordpress/'
        slash_ari = self.wp.validate_wp_dir(test_data)
        slash_no = self.wp.validate_wp_dir(test_data[:-1])
        self.assertEqual(
            slash_ari,
            slash_no,
            "パス指定の自動修正ができているかどうか"
        )

    def test_get_download_file(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        os.mkdir("%sasset/" % self.wp.tmp_dir)
        wp_file = 'wp-includes/functions.php'
        abs_path = "%swordpress/%s" % (self.wp.tmp_dir, wp_file)
        df = self.wp.get_download_file(wp_file)
        self.assertEqual(
            abs_path,
            df,
            "絶対パスの推測がうまくいくかどうか"
        )

    def test_get_file_list(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        download_dir = '%swordpress' % self.wp.tmp_dir
        os.mkdir("%sasset/" % self.wp.tmp_dir)
        asset_dir = '%sasset/wordpress' % self.wp.tmp_dir
        shutil.copytree(download_dir, asset_dir)
        # 間違ったディレクトリの場合の処理
        file_list = self.wp.get_file_list(asset_dir + "aa")
        self.assertEqual(
            1,
            len(file_list),
            "ディレクトリ指定が間違った場合の処理"
        )
        # 正当処理
        file_list = self.wp.get_file_list(asset_dir)
        self.assertNotEqual(
            1,
            len(file_list),
            "ディレクトリ指定が合ってた場合の処理"
        )

    def test_is_file_ok(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        download_file = 'wp-includes/functions.php'
        is_file_ok = self.wp.is_file_ok(download_file)
        self.assertTrue(is_file_ok["result"])
        backdoor_file = 'wp-includes/backdoor.php'
        is_file_ok_backdoor = self.wp.is_file_ok(backdoor_file)
        self.assertFalse(is_file_ok_backdoor["result"])

    def test_is_file_modified(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        download_dir = '%swordpress' % self.wp.tmp_dir
        os.mkdir("%sasset/" % self.wp.tmp_dir)
        asset_dir = '%sasset/wordpress' % self.wp.tmp_dir
        shutil.copytree(download_dir, asset_dir)
        download_file = 'wp-includes/functions.php'
        is_file_modified = self.wp.is_file_modified(asset_dir, download_file)
        self.assertTrue(
            is_file_modified["result"],
            "ファイルが同一であることを確認できているかどうか"
        )
        wp_abs_path = "%s/%s" % (asset_dir, download_file)
        wp_abs_bk_path = "%s/%s.bak" % (asset_dir, download_file)
        # ファイルを移動
        shutil.copyfile(wp_abs_path, wp_abs_bk_path)
        f = open(wp_abs_path, 'a')
        f.write('changed\n')
        f.close()
        is_hacked = self.wp.is_file_modified(asset_dir, download_file)
        self.assertFalse(
            is_hacked["result"],
            "ファイルが改ざんされていることを検知できているかどうか"
        )

    def test_is_file_binary(self):
        self.check_tmp = self.wp.check_tmp()
        self.wp.version_info = self.version_info
        response_data = self.wp.download_wp()
        self.wp.extract_wp(response_data)
        download_dir = '%swordpress' % self.wp.tmp_dir
        os.mkdir("%sasset/" % self.wp.tmp_dir)
        asset_dir = '%sasset/wordpress' % self.wp.tmp_dir
        shutil.copytree(download_dir, asset_dir)
        dir_name = asset_dir + '/wp-content/uploads'
        file_list = self.wp.get_file_list(dir_name, False)
        for file_name in file_list:
            file_path = "%s/%s" % (dir_name, file_name)
            is_file_binary = self.wp.is_file_binary(file_path)
            if os.path.isfile(file_path):
                if 'b.png' in file_path:
                    # 不正なファイル
                    self.assertFalse(
                        is_file_binary,
                        "不正なファイルの検知"
                    )
                else:
                    self.assertTrue(
                        is_file_binary,
                        "正常なファイルの検知"
                    )
            else:
                self.assertTrue(
                    is_file_binary,
                    "ディレクトリの検知"
                )

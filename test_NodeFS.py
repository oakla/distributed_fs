from src import client_model
import unittest

FS_001_ROOT = "test/test_file_systems/001"
FS_002_EMPTY_ROOT = "test/test_file_systems/002-empty"

class TestDirectoryQueries(unittest.TestCase):

    def test_n_items(self):
        node_001 = client_model.NodeFS(FS_001_ROOT)
        node_001_root_info = node_001.get_directory_info()
        node_001_root_child_folder_info = node_001_root_info["a_folder"]            
        self.assertEqual(node_001_root_child_folder_info["n_items"], "5")

    def test_sha256_hash(self):
        expected = "71944d7430c461f0cd6e7fd10cee7eb72786352a3678fc7bc0ae3d410f72aece"
        node_001 = client_model.NodeFS(FS_001_ROOT)
        node_001_root_info = node_001.get_directory_info()
        node_001_root_child_mp4_info = node_001_root_info["file_example_MP4_480_1_5MG.mp4"] 
        self.assertEqual(node_001_root_child_mp4_info["sha256_hash"], expected)


    # todo: test empty dir
if __name__ == "__main__":
    unittest.main()
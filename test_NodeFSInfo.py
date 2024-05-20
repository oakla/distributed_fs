from src import server_model

fs_info_dict = {
    "path": "/",
    "contents": [
        {
            "name": "always look on the bright side of life.txt",
            "mtime": 1715773114.6726763,
            "type": "file",
            "n_items": "",
            "sha256_hash": "a8a81d55f87e4e6978f2fdb291f39d170b864fb2be5d499820d0cfdaa354b708",
        },
        {
            "name": "a_folder",
            "mtime": 1715915262.277324,
            "type": "directory",
            "n_items": "5",
            "sha256_hash": "",
        },
        {
            "name": "file_example_MP4_480_1_5MG.mp4",
            "mtime": 1715827514.3208964,
            "type": "file",
            "n_items": "",
            "sha256_hash": "71944d7430c461f0cd6e7fd10cee7eb72786352a3678fc7bc0ae3d410f72aece",
        },
        {
            "name": "hello.txt",
            "mtime": 1715773125.9826744,
            "type": "file",
            "n_items": "",
            "sha256_hash": "b60eaf09e14454fe5135c8fd9aeca44a49115f5c9ed8d54db7add6ce58e6d529",
        },
        {
            "name": "hello_again.txt - Shortcut.lnk",
            "mtime": 1715915257.7873247,
            "type": "file",
            "n_items": "",
            "sha256_hash": "76dfbead5c2b09b7e914e3113f4dae82795b8bc812d01a6d37d8d2265fa966e0",
        },
        {
            "name": "comedic_genres_wikipedia.md",
            "mtime": 1715817119.717139,
            "type": "file",
            "n_items": "",
            "sha256_hash": "b4b31203cbe599a3655523134f1baea4d1e0bf36cf8f769da02de70d8344a11e",
        },
        {
            "name": "file_example_MP4_480_1_5MG.mp4:Zone.Identifier",
            "mtime": 1715827514.3208964,
            "type": "file",
            "n_items": "",
            "sha256_hash": "1717fb85e1193ff5ff7eae7e5d5e2a99fbb804c581e705e29892586f404569a1",
        },
    ],
}

node_fs_info = server_model.NodeFSInfo(("127.0.0.1", "65342"), fs_info_dict)


print(node_fs_info.get_top_level_info_string())

default_path = "bot/library"

def get_lib_path(user_id, title):
    return default_path + "/" + str(user_id) + "_" + title + ".pdf"

def book_upload_disk(path, content: bytes):
    with open(path, "wb") as file:
        file.write(content)
from urllib.parse import unquote


def get_file_name(file):
    return unquote(str(file)[str(file).rfind("/") + 1 : :])

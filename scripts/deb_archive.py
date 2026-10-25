"""Read .deb metadata without extracting files or requiring Linux tools."""
import io
import tarfile


def members(path):
    data = path.read_bytes()
    if data[:8] != b"!<arch>\n":
        raise ValueError(f"Invalid Debian archive: {path}")
    offset, result = 8, {}
    while offset < len(data):
        header = data[offset:offset + 60]
        if len(header) != 60 or header[58:] != b"`\n":
            raise ValueError(f"Invalid ar header: {path}")
        name = header[:16].decode("ascii").strip()
        size = int(header[48:58])
        value = data[offset + 60:offset + 60 + size]
        if len(value) != size:
            raise ValueError(f"Truncated ar member: {path}")
        offset += 60 + size + size % 2
        if name.startswith("#1/"):
            length = int(name[3:])
            name, value = value[:length].decode().rstrip("\0"), value[length:]
        result[name.rstrip("/")] = value
    return result


def tar_member(path, archive_prefix, member):
    archives = [v for k, v in members(path).items() if k.startswith(archive_prefix)]
    if len(archives) != 1:
        raise ValueError(f"Expected one {archive_prefix} archive: {path}")
    with tarfile.open(fileobj=io.BytesIO(archives[0])) as archive:
        matches = [m for m in archive if m.name.removeprefix("./") == member]
        if len(matches) != 1 or not matches[0].isfile():
            raise ValueError(f"Missing regular member {member}: {path}")
        return archive.extractfile(matches[0]).read()


def parse_control(text):
    fields, key = {}, None
    for line in text.splitlines():
        if line.startswith((" ", "\t")) and key:
            fields[key] += "\n" + line
        elif line:
            key, value = line.split(":", 1)
            fields[key] = value.lstrip()
    return fields


def control(path):
    return parse_control(tar_member(path, "control.tar", "control").decode("utf-8"))

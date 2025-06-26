import subprocess

m3u8_url = "https://ivod-lyvod.cdn.hinet.net/vod_1/_definst_/mp4:1MClips/1b546098ab7db506b631e2a49f39fdc58be1699f4405fe9ff4d9bffd44bdf5d95ada283277b8f26e5ea18f28b6918d91.mp4/playlist.m3u8"
output_file = "legislative_meeting.mp4"

subprocess.run([
    "ffmpeg",
    "-headers", "Referer: https://ivod.ly.gov.tw/\r\n",
    "-i", m3u8_url,
    "-c", "copy",
    output_file
])


# readyPlayer("https://ivod-lyvod.cdn.hinet.net/vod_1/_definst_/mp4:1MClips/1b546098ab7db506b631e2a49f39fdc58be1699f4405fe9ff4d9bffd44bdf5d95ada283277b8f26e5ea18f28b6918d91.mp4/playlist.m3u8","16_9");

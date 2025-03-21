from pytubefix import YouTube
import subprocess
import os
import ssl
import certifi

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def download_video(vid_url, path):
    yt = YouTube(vid_url)
    vid_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res='720p').first()
    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

    if vid_stream is None:
        vid_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').first()
    vid_stream.download(output_path=path, filename='video.mp4')
    audio_stream.download(output_path=path, filename='audio.mp4')

    return yt.title

def download_audio(vid_url, path):
    yt = YouTube(vid_url)
    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
    audio_stream.download(output_path=path, filename=yt.title + '.mp3')

def remux_streams(path, output_filename):
    video_path = os.path.join(path, 'video.mp4')
    audio_path = os.path.join(path, 'audio.mp4')
    output_path = os.path.join(path, output_filename)

    command = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c', 'copy',
        output_path
    ]

    subprocess.run(command, check=True)
    os.remove(video_path)
    os.remove(audio_path)
    print(f'Remuxing complete: {output_path}')


if __name__ == "__main__":
    url = input('Input URL:\n')
    path = "C:/Users/zakin/Downloads"
    file_extension = ''
    while file_extension != 'mp3' and file_extension != 'mp4':
        file_extension = input('mp3 or mp4?\n')

    if file_extension == 'mp3':
        download_audio(url, path)

    elif file_extension == 'mp4':
        title = download_video(url, path)
        output_filename = title + ".mp4"
        remux_streams(path, output_filename)
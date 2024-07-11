import os


class AudioConverter:
    @staticmethod
    def convert_webm_to_wav(input_path: str, output_path: str) -> None:
        result = os.system(  # noqa: F841
            f"ffmpeg -y -i {input_path} -vn -ar 44100 -ac 2 -b:a 192k {output_path}"
        )

        print(result)

from youtube_transcript_api import YouTubeTranscriptApi

class YoutubeVideoScrapperTool:

    def getVideoID(self, url: str) -> str:
        """
        This function gets the video ID from the URL provided by the user.
        """
        try:
            if "youtu.be" in url:
                return url.split("/")[-1]
            elif "youtube.com" in url:
                return url.split("v=")[1].split("&")[0]
            else:
                raise ValueError("Invalid YouTube URL format.")
        except IndexError:
            raise ValueError("Invalid YouTube URL format.")

    def get_transcription(self, video_id: str) -> dict:
        """
        Gets the transcript of the video directly from YouTube (default=en).
        Returns a dictionary.
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch transcription: {e}")

    def execute(self, url: str = ""):
        """
        Main function to execute the tool.
        """
        if not url:
            print("No URL provided.")
            return

        try:
            video_id = self.getVideoID(url)
            transcript = self.get_transcription(video_id)

            print('YoutubeVideoScrapperTool:', transcript)
            return transcript

        except Exception as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    scraper = YoutubeVideoScrapperTool()
    url = "https://www.youtube.com/watch?v=Oo8-nEuDBkk"
    scraper.execute(url)
    print('------------')
    urv2 = 'https://youtu.be/argpSxB1NQE?si=djxfU0ObgHatQU7Q&t=6003'
    scraper.execute(url)
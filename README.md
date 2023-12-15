# GoPro Cloud Video Downloader

This Python application allows you to download all the videos available on a public cloud link from GoPro using Selenium and the Chrome WebDriver.

## Prerequisites

Before using this application, ensure you have the following installed:

- Python 3.x
- Chrome WebDriver (download the appropriate version for your Chrome browser)

## Setup

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/c-louis/GoProCloudDownloader.git
    cd GoProCloudDownloader
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Open the `main.py` file.
2. Modify the `URLs` variable to contain the GoPro cloud link you want to download videos from. (You can specify multiple URLs by splitting them with `;`
3. Modify the `Download Path` by either typing it or using the button to do so.
4. Click on explore and the program will search for all the videos on your links. Will then load them and then give you the possibility to download all of them. (Download All option)

## Executable Release

If you prefer not to run the Python script directly, you can download the executable file for this application from the [Releases](https://github.com/c-louis/GoProCloudDownloader/releases) section.
- The executable simplifies the usage by running the application without requiring Python or additional dependencies.
- The executable will be detected by anti-virus softwares as potentionaly harmful, it is not.


## Important Notes

- Make sure your internet connection is stable during the download, the program is not very responsive to canceled download and might wait forever.
- The script might take some time depending on the number and size of the videos available for download.
- Ensure that you have sufficient storage space to save the downloaded videos.
- This application is designed for public GoPro cloud links and wont work with private links.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or create a pull request.

## License

This project is licensed under the [GPL-3.0 license](LICENSE).

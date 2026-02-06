from huggingface_hub import snapshot_download
import os

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "1200"
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com" 

def download_model(local_dir, repo_id="tencent/SongGeneration", revision="87bccf1"):
    downloaded_path = snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        revision=revision,
        token=os.environ.get("HF_TOKEN"), 
        ignore_patterns=['.git*']
    )
    print(f"File downloaded to:{downloaded_path}")


if __name__ == '__main__':
    download_model('.')
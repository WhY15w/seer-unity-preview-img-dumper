import PQueue from "p-queue";
import Downloader from "./Downloader";
import YooVersionManager from "./YooVersionManager";
import { DownloadParams } from "./types";

export default class Updater {
  constructor(
    private name: string,
    private desc: string,
    private versionManager: YooVersionManager,
    private downloader: Downloader,
    private postprocess?: (data: Buffer) => Buffer
  ) {}

  private log(msg: string) {
    console.log(`更新器[${this.name}]: ${msg}`);
  }

  /**
   * 检查并更新文件
   * @param semaphoreLimit 并发限制
   * @param includeKeywords 只下载包含这些关键字的文件（可选）
   */
  async update(semaphoreLimit?: number, includeKeywords?: string[]) {
    this.log("检查更新...");
    const manifest = await this.versionManager.generateUpdateManifest();
    if (!manifest) return this.log("没有需要更新的文件");

    let filesToUpdate = Array.from(manifest.items);

    if (includeKeywords && includeKeywords.length > 0) {
      filesToUpdate = filesToUpdate.filter(([filename]) => {
        return includeKeywords.some((keyword) =>
          filename.toLowerCase().includes(keyword.toLowerCase())
        );
      });

      this.log(`应用筛选条件: 包含关键字 ${includeKeywords.join(", ")}`);
      this.log(`筛选后需要更新的文件数量: ${filesToUpdate.length}`);

      if (filesToUpdate.length === 0) {
        return this.log("没有符合筛选条件的文件需要更新");
      }
    } else {
      this.log(`需要更新文件数量: ${filesToUpdate.length}`);
    }

    const tasks: DownloadParams[] = filesToUpdate.map(([fn, item]) => ({
      url: item.remoteFilename,
      filename: fn,
      md5: item.fileHash,
    }));

    const semaphore = semaphoreLimit
      ? new PQueue({ concurrency: semaphoreLimit })
      : undefined;

    await this.downloader.downloads(tasks, this.postprocess, semaphore);
    this.versionManager.saveManifestToLocal(manifest);
    this.log("更新完成");
  }

  async getVersionInfo() {
    return {
      local: this.versionManager.loadLocalVersion(),
      remote: await this.versionManager.getRemoteVersion(),
    };
  }
}

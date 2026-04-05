
import os
import shutil
import libcore_hng.exceptions.filesystem_exception as FileSystemException
import libcore_hng.utils.app_logger as app_logger
from typing import List, Optional
from libcore_hng.utils.enums import OnConflict

class FileRenamer:
    """
    指定されたディレクトリ内のファイルを一括でリネームするためのユーティリティクラス。

    Parameters
    ----------
    directory : str
        対象ファイルが格納されているディレクトリのパス。
    """

    def __init__(self, directory: str):
        if not os.path.isdir(directory):
            raise ValueError(f"Specified directory not found: {directory}")
        self.directory = directory
        self._logger = app_logger

    def _backup_file(self, source_path: str, backup_directory: str) -> str:
        """
        単一のファイルをバックアップディレクトリにコピーする。

        Parameters
        ----------
        source_path : str
            バックアップするファイルの元のパス。
        backup_directory : str
            ファイルをコピーするバックアップディレクトリのパス。

        Returns
        -------
        str
            バックアップされたファイルの新しいパス。

        Raises
        ------
        FileSystemException
            ファイル操作中にエラーが発生した場合。
        """
        os.makedirs(backup_directory, exist_ok=True)
        destination_path = os.path.join(backup_directory, os.path.basename(source_path))
        try:
            shutil.copy2(source_path, destination_path)
            self._logger.info(f"Backed up \'{source_path}\' to \'{destination_path}\'")
            return destination_path
        except Exception as e:
            msg = f"Failed to backup \'{source_path}\' to \'{destination_path}\' . Error: {e}"
            self._logger.error(msg)
            raise FileSystemException(msg) from e

    def rename_files(
        self,
        prefix: str = "",
        suffix: str = "",
        extension: Optional[str] = None,
        sequence_format: str = "{:04d}",
        start_index: int = 1,
        dry_run: bool = False,
        on_conflict: OnConflict = OnConflict.SKIP,
        backup_directory: Optional[str] = None,
    ) -> List[dict]:
        """
        指定された条件に基づいてファイルをリネームする。

        Parameters
        ----------
        prefix : str, optional
            リネーム後のファイル名に付与するプレフィックス。デフォルトは空文字列。
        suffix : str, optional
            リネーム後のファイル名に付与するサフィックス。デフォルトは空文字列。
        extension : Optional[str], optional
            対象ファイルをフィルタリングする拡張子 (例: "txt", "jpg")。None の場合はすべてのファイルを対象とする。デフォルトは None。
        sequence_format : str, optional
            連番のフォーマット文字列 (例: "{:03d}" -> 001, "{:04d}" -> 0001)。デフォルトは "{:04d}"。
        start_index : int, optional
            連番の開始インデックス。デフォルトは 1。
        dry_run : bool, optional
            True の場合、実際にはリネームせず、変更内容のみをリストで返す。デフォルトは False。
        on_conflict : OnConflict, optional
            名前衝突時の挙動。
            OnConflict.ERROR: エラーを発生させる (デフォルト)。
            OnConflict.SKIP: 既存ファイルをスキップする。
            OnConflict.OVERWRITE: 既存ファイルを上書きする。
        backup_directory : Optional[str], optional
            ファイルをバックアップするディレクトリのパス。None の場合はバックアップしない。デフォルトは None。

        Returns
        -------
        List[dict]
            実行された、または実行予定のリネーム操作のリスト。
            各辞書は `{"old_name": str, "new_name": str, "status": str, "backup_path": Optional[str]}` の形式。（`backup_path`は追加）

        Raises
        ------
        FileSystemException
            ファイル操作中にエラーが発生した場合。
        ValueError
            不正な `on_conflict` 値が指定された場合。
        """
        if on_conflict not in [OnConflict.ERROR, OnConflict.SKIP, OnConflict.OVERWRITE]:
            raise ValueError("on_conflict must be one of 'error', 'skip', or 'overwrite'.")

        if backup_directory and not dry_run:
            self._logger.info(f"Backup directory specified: \'{backup_directory}\'. Files will be backed up.")

        self._logger.info(f"Starting file rename in directory \'{self.directory}\' (dry_run: {dry_run})")
        renamed_files: List[dict] = []
        files_to_rename = []
        
        # 対象ファイルのリストアップ
        sorted_files = sorted(os.listdir(self.directory))
        for _, filename in enumerate(sorted_files):
            if os.path.isfile(os.path.join(self.directory, filename)):
                _, ext = os.path.splitext(filename)
                # 拡張子から "." を除去
                current_ext = ext[1:] if ext else "" 

                if extension and current_ext != extension:
                    self._logger.debug(f"Skipped: Extension mismatch for \'{filename}\' (expected: \'{extension}\', actual: \'{current_ext}\')")
                    continue

                files_to_rename.append(filename)

        if not files_to_rename:
            self._logger.info("No files found to rename.")
            return []

        # リネーム処理
        for file_no, old_filename in enumerate(sorted(files_to_rename)):
            
            # ファイル名と拡張子を分割
            _, ext = os.path.splitext(old_filename)
            
            # 新しいファイル名の構築
            sequence_number = sequence_format.format(start_index + file_no)
            new_filename_base = f"{prefix}{sequence_number}{suffix}"
            new_filename = f"{new_filename_base}{ext}"
            
            # ファイルのフルパスを構築
            old_path = os.path.join(self.directory, old_filename)
            new_path = os.path.join(self.directory, new_filename)

            status = ""
            backup_path: Optional[str] = None

            if os.path.exists(new_path):
                # 名前衝突時の処理
                if on_conflict == OnConflict.ERROR:
                    msg = f"Conflict Error: Target file \'{new_filename}\' already exists."
                    self._logger.error(msg)
                    raise FileSystemException(msg)
                elif on_conflict == OnConflict.SKIP:
                    self._logger.warning(f"Skipped: Rename \'{old_filename}\' to \'{new_filename}\' skipped due to conflict.")
                    status = "skipped (conflict)"
                    renamed_files.append({"old_name": old_filename, "new_name": new_filename, "status": status, "backup_path": backup_path}) # 変更
                    continue
                elif on_conflict == OnConflict.OVERWRITE:
                    self._logger.warning(f"Overwriting: Existing file \'{new_filename}\' will be replaced.")
                    status = "overwritten"

            if not dry_run:
                # バックアップ実行
                if backup_directory:
                    backup_path = self._backup_file(old_path, backup_directory)

                try:
                    # ファイルをリネームする
                    os.rename(old_path, new_path)
                    self._logger.info(f"Rename successful: \'{old_filename}\' -> \'{new_filename}\'")
                    status = "renamed"
                except OSError as e:
                    error_msg = f"Failed to rename: \'{old_filename}\' -> \'{new_filename}\'. Error: {e}"
                    self._logger.error(error_msg)
                    raise FileSystemException(error_msg) from e
            else:
                self._logger.info(f"[Dry Run] \'{old_filename}\' -> \'{new_filename}\' (status: {status if status else 'would be renamed'}) ")
                status = status if status else "would be renamed"

            renamed_files.append({"old_name": old_filename, "new_name": new_filename, "status": status, "backup_path": backup_path})

        self._logger.info("File renaming process completed.")
        return renamed_files

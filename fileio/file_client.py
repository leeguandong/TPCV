'''
@Time    : 2022/3/1 15:37
@Author  : leeguandon@gmail.com
'''
import os
import tpcv
import os.path as osp
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Iterable, Iterator, Optional, Tuple, Union
from contextlib import contextmanager


class BaseStorageBackend(metaclass=ABCMeta):
    """Abstract class of storage backends.

    All backends need to implement two apis: ``get()`` and ``get_text()``.
    ``get()`` reads the file as a byte stream and ``get_text()`` reads the file
    as texts.
    """

    # a flag to indicate whether the backend can create a symlink for a file
    _allow_symlink = False

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def allow_symlink(self):
        return self._allow_symlink

    @abstractmethod
    def get(self, filepath):
        pass

    @abstractmethod
    def get_text(self, filepath):
        pass


class HardDiskBackend(BaseStorageBackend):
    """Raw hard disks storage backend."""

    _allow_symlink = True

    def get(self, filepath: Union[str, Path]) -> bytes:
        """Read data from a given ``filepath`` with 'rb' mode.

        Args:
            filepath (str or Path): Path to read data.

        Returns:
            bytes: Expected bytes object.
        """
        with open(filepath, 'rb') as f:
            value_buf = f.read()
        return value_buf

    def get_text(self,
                 filepath: Union[str, Path],
                 encoding: str = 'utf-8') -> str:
        """Read data from a given ``filepath`` with 'r' mode.

        Args:
            filepath (str or Path): Path to read data.
            encoding (str): The encoding format used to open the ``filepath``.
                Default: 'utf-8'.

        Returns:
            str: Expected text reading from ``filepath``.
        """
        with open(filepath, 'r', encoding=encoding) as f:
            value_buf = f.read()
        return value_buf

    def put(self, obj: bytes, filepath: Union[str, Path]) -> None:
        """Write data to a given ``filepath`` with 'wb' mode.

        Note:
            ``put`` will create a directory if the directory of ``filepath``
            does not exist.

        Args:
            obj (bytes): Data to be written.
            filepath (str or Path): Path to write data.
        """
        tpcv.mkdir_or_exist(osp.dirname(filepath))
        with open(filepath, 'wb') as f:
            f.write(obj)

    def put_text(self,
                 obj: str,
                 filepath: Union[str, Path],
                 encoding: str = 'utf-8') -> None:
        """Write data to a given ``filepath`` with 'w' mode.

        Note:
            ``put_text`` will create a directory if the directory of
            ``filepath`` does not exist.

        Args:
            obj (str): Data to be written.
            filepath (str or Path): Path to write data.
            encoding (str): The encoding format used to open the ``filepath``.
                Default: 'utf-8'.
        """
        tpcv.mkdir_or_exist(osp.dirname(filepath))
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(obj)

    def remove(self, filepath: Union[str, Path]) -> None:
        """Remove a file.

        Args:
            filepath (str or Path): Path to be removed.
        """
        os.remove(filepath)

    def exists(self, filepath: Union[str, Path]) -> bool:
        """Check whether a file path exists.

        Args:
            filepath (str or Path): Path to be checked whether exists.

        Returns:
            bool: Return ``True`` if ``filepath`` exists, ``False`` otherwise.
        """
        return osp.exists(filepath)

    def isdir(self, filepath: Union[str, Path]) -> bool:
        """Check whether a file path is a directory.

        Args:
            filepath (str or Path): Path to be checked whether it is a
                directory.

        Returns:
            bool: Return ``True`` if ``filepath`` points to a directory,
            ``False`` otherwise.
        """
        return osp.isdir(filepath)

    def isfile(self, filepath: Union[str, Path]) -> bool:
        """Check whether a file path is a file.

        Args:
            filepath (str or Path): Path to be checked whether it is a file.

        Returns:
            bool: Return ``True`` if ``filepath`` points to a file, ``False``
            otherwise.
        """
        return osp.isfile(filepath)

    def join_path(self, filepath: Union[str, Path],
                  *filepaths: Union[str, Path]) -> str:
        """Concatenate all file paths.

        Join one or more filepath components intelligently. The return value
        is the concatenation of filepath and any members of *filepaths.

        Args:
            filepath (str or Path): Path to be concatenated.

        Returns:
            str: The result of concatenation.
        """
        return osp.join(filepath, *filepaths)

    @contextmanager
    def get_local_path(
            self, filepath: Union[str, Path]) -> Iterable[Union[str, Path]]:
        """Only for unified API and do nothing."""
        yield filepath

    def list_dir_or_file(self,
                         dir_path: Union[str, Path],
                         list_dir: bool = True,
                         list_file: bool = True,
                         suffix: Optional[Union[str, Tuple[str]]] = None,
                         recursive: bool = False) -> Iterator[str]:
        """Scan a directory to find the interested directories or files in
        arbitrary order.

        Note:
            :meth:`list_dir_or_file` returns the path relative to ``dir_path``.

        Args:
            dir_path (str | Path): Path of the directory.
            list_dir (bool): List the directories. Default: True.
            list_file (bool): List the path of files. Default: True.
            suffix (str or tuple[str], optional):  File suffix
                that we are interested in. Default: None.
            recursive (bool): If set to True, recursively scan the
                directory. Default: False.

        Yields:
            Iterable[str]: A relative path to ``dir_path``.
        """
        if list_dir and suffix is not None:
            raise TypeError('`suffix` should be None when `list_dir` is True')

        if (suffix is not None) and not isinstance(suffix, (str, tuple)):
            raise TypeError('`suffix` must be a string or tuple of strings')

        root = dir_path

        def _list_dir_or_file(dir_path, list_dir, list_file, suffix,
                              recursive):
            for entry in os.scandir(dir_path):
                if not entry.name.startswith('.') and entry.is_file():
                    rel_path = osp.relpath(entry.path, root)
                    if (suffix is None
                        or rel_path.endswith(suffix)) and list_file:
                        yield rel_path
                elif osp.isdir(entry.path):
                    if list_dir:
                        rel_dir = osp.relpath(entry.path, root)
                        yield rel_dir
                    if recursive:
                        yield from _list_dir_or_file(entry.path, list_dir,
                                                     list_file, suffix,
                                                     recursive)

        return _list_dir_or_file(dir_path, list_dir, list_file, suffix,
                                 recursive)


class FileClient:
    _backends = {
        'disk': HardDiskBackend,
    }

    _instances = {}

    def __new__(cls, backend=None, prefix=None, **kwargs):
        if backend is None and prefix is None:
            backend = "disk"

        _instance = super().__new__(cls)
        _instance.client = cls._backends[backend](**kwargs)
        cls._instances[f'{backend}:{prefix}'] = _instance
        return _instance

    @property
    def name(self):
        return self.client.name

    @property
    def allow_symlink(self):
        return self.client.allow_symlink

    @staticmethod
    def infer_client(cls,
                     file_client_args: Optional[dict] = None,
                     uri: Optional[Union[str, Path]] = None) -> 'FileClient':
        if file_client_args is None:
            return cls(prefix=None)
        else:
            return cls(**file_client_args)

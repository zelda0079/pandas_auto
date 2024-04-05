
import itertools
from typing import Generator, List, Iterable


class CodeFormatter(object):

    @staticmethod
    def type2str(v):
        if isinstance(v, str):
            return f'"{v}"' if "'" in v else f"'{v}'"

        return str(v)

    def to_code(self, method_name: str, args, kws) -> str:
        raise NotImplementedError


class StandardCodeFormatter(CodeFormatter):

    def convert_args_type(self, args: list) -> Generator[str, None, None]:
        return (
            CodeFormatter.type2str(a)
            for a in args
        )

    def convert_kws_type(self, kws: dict) -> Generator[str, None, None]:
        return (
            f'{k} = {CodeFormatter.type2str(v)}'
            for k, v in kws.items()
        )

    def do_to_code(self, method_name: str, args: Iterable[str], kws: Iterable[str]):
        raise NotImplementedError

    def to_code(self, method_name: str, args: list, kws: dict) -> str:
        args2type = self.convert_args_type(args)
        kws2type = self.convert_kws_type(kws)

        return self.do_to_code(method_name, args2type, kws2type)


class MethodCodeFormatter(StandardCodeFormatter):
    def do_to_code(self, method_name: str, args: Iterable[str], kws: Iterable[str]):
        smr_args = ','.join(itertools.chain(args, kws))
        return f'.{method_name}({smr_args})'


class GetItemCodeFormatter(StandardCodeFormatter):
    def do_to_code(self, method_name: str, args: Iterable[str], kws: Iterable[str]):
        smr_args = ','.join(itertools.chain(args, kws))
        return f'[{smr_args}]'


class OperatorCodeFormatter(StandardCodeFormatter):
    def do_to_code(self, operator: str, args: Iterable[str], kws: Iterable[str]):
        other = list(args)[0]
        return f'{operator}{other}'


class ImportCodeFormatter(CodeFormatter):

    pass


if __name__ == "__main__":
    pass

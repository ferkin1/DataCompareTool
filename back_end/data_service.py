import pandas as pd
import os
import json
import traceback
from typing import List, Sequence, Union, Dict, Optional, Tuple

class DataService():
    def __init__(self, export_path:str):
        self.export_path:str = export_path
        self.Cols = Union[str, Sequence[str]]

    def json_reader(self, path:str) -> pd.DataFrame:
        try:
            return pd.read_json(path)
        except ValueError as e:
            if "Trailing data" in str(e) or "Expected object or value" in str(e):
                return pd.read_json(path, lines=True)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            if isinstance(raw, dict):
                # if top-level is dict, try to normalize based on a likely array
                # prefer first value if list-like
                first_key = next(iter(raw))
                if first_key is not None and isinstance(raw[first_key], list):
                    return pd.json_normalize(raw[first_key])
                # else flatten
                return pd.json_normalize(raw)
            elif isinstance(raw, list):
                return pd.json_normalize(raw)
            else:
                raise RuntimeError(f"Unsupported JSON structure type: {type(raw)}")

    def get_data(self, data_path:str) -> pd.DataFrame:
        txt_list = ['.csv', '.txt', '.tsv']
        excel_list = ['.xlsx', '.xls', '.xlsm', '.xlsb', '.ods']
        other_formats = {
            '.json': self.json_reader,
            '.html': lambda path: pd.read_html(path)[0],
            '.parquet': pd.read_parquet,
            '.pkl': pd.read_pickle,
            '.dta': pd.read_stata,
            '.sas7bdat': pd.read_sas,
            '.xpt': pd.read_sas,
            '.feather': pd.read_feather
        }

        try:
            ext = os.path.splitext(data_path)[1].lower()
            if ext in txt_list:
                sep = "\t" if ext == ".tsv" else ","
                data = pd.read_csv(data_path, sep=sep, low_memory=False)
                return data

            elif ext in excel_list:
                engine = None
                if ext == ".xlsb":
                    engine = "pyxlsb"
                data = pd.read_excel(data_path, engine=engine)
                return data

            elif ext in other_formats:
                reader_func = other_formats.get(ext)
                data = reader_func(data_path)
                if isinstance(data, list):
                    if not data:
                        raise RuntimeError("read_html returned no tables")
                    data = data[0]
                return data

            raise RuntimeError(f"Unsupported file type: {ext}")

        except FileNotFoundError:
            raise RuntimeError("File could not be found")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}\n\n{traceback.format_exc()}")

    def compare_columns(self, data_1: pd.DataFrame, data_2: pd.DataFrame,
                        columns_1: str|List, columns_2: str|List,
                        *, suffixes: Tuple[str, str] = ("_A", "_B"),
                        keep_cols_1: Optional[Sequence[str]] = None,
                        keep_cols_2: Optional[Sequence[str]] = None,
                        validate: Optional[str] = None,
                        normalize_str: bool = False) -> Dict[str, pd.DataFrame]:

        if isinstance(columns_1, str):
            cols_1 = [columns_1]
        else:
            cols_1 = list(columns_1)
        if isinstance(columns_2, str):
            cols_2 = [columns_2]
        else:
            cols_2 = list(columns_2)

        if len(cols_1) != len(cols_2):
            raise ValueError("Columns_1 and Columns_2 must have the same number of keys")

        missing_1 = [c for c in cols_1 if c not in data_1.columns]
        missing_2 = [c for c in cols_2 if c not in data_2.columns]
        if missing_1 or missing_2:
            raise KeyError(f"Missing columns. A-side: {missing_1} || B-side: {missing_2}")

        if normalize_str:
            df1 = data_1.copy()
            df2 = data_2.copy()
            for c in cols_1:
                if pd.api.types.is_string_dtype(df1[c]):
                    df1[c] = df1[c].astype("string").str.strip().str.lower()
            for c in cols_2:
                if pd.api.types.is_string_dtype(df2[c]):
                    df2[c] = df2[c].astype("string").str.strip().str.lower()
        else:
            df1 = data_1
            df2 = data_2

        if keep_cols_1 is not None:
            keep_1 = list(dict.fromkeys([*cols_1, *keep_cols_1]))
            df1 = df1[keep_1]
        if keep_cols_2 is not None:
            keep_2 = list(dict.fromkeys([*cols_2, *keep_cols_2]))
            df2 = df2[keep_2]

        merged_df = pd.merge(df1, df2,
                             left_on=cols_1,
                             right_on=cols_2,
                             how="outer",
                             suffixes=suffixes,
                             indicator=True,
                             validate=validate
                             )
        matches = merged_df[merged_df["_merge"] == "both"].copy()
        left_only = merged_df[merged_df["_merge"] == "left_only"].copy()
        right_only = merged_df[merged_df["_merge"] == "right_only"].copy()

        return {
            "merged": merged_df,
            "matches": matches,
            "left_only": left_only,
            "right_only": right_only
        }

if __name__ == "__main__":
    datacomp = DataService("")
    data = datacomp.get_data(".venv/resources/dataset_a.csv")
    # print(data.head(10))
    data2 = datacomp.get_data(".venv/resources/dataset_b.xlsx")
    # print(data2.head(10))
    res = datacomp.compare_columns(data, data2, "id", "id")
    print(res["matches"])
    print(res["left_only"])
    print(res["right_only"])
    print(res["merged"])

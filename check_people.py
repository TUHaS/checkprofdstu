import argparse
import csv
import logging
from pathlib import Path

import vk
import pandas as pd
from tqdm import tqdm

from config import (
    SECRET_KEY, API_VERSION, STATUS_ERROR, STATUS_DUPLICATE, COLUMN_NAME_VK_ID,
    STATUS_GROUP_MEMBER, COLUMN_NAME_BOOKNUMBER, GROUP_ID, COLUMN_NAME_STATUS,
    COLUMN_NAME_ERROR_MSG, STATUS_NOT_MEMBER
)

logger = logging.getLogger(__file__)


def get_user_id(vk_api: vk.api.API, vk_id: str) -> int:
    formatted_id = vk_id.replace(" ", "").replace("@", "")
    id_split = formatted_id.split("/")
    target_id = id_split[-1] if id_split[-1] != "" else id_split[-2]
    logger.info(f"file-id: '{vk_id}'. Transformed id: '{target_id}'")
    user_info = vk_api.users.get(user_ids=[target_id], v=API_VERSION)
    if len(user_info) > 1:
        msg = f"Invalid length of user info list. id={vk_id}"
        raise ValueError(msg)
    valid_user_id = user_info[0]["id"]
    logger.info(f"file-id: '{vk_id}'. Valid VK id: '{valid_user_id}'")
    return valid_user_id


def main(file_path: str, result_path: str) -> None:
    session = vk.Session(access_token=SECRET_KEY)
    vk_api = vk.API(session)
    members = vk_api.groups.getMembers(group_id=GROUP_ID, v=API_VERSION)
    data = members["items"]
    count = members["count"] // 1000
    for i in tqdm(range(1, count + 1),
                  desc=f"Get ids of group members (id={GROUP_ID})"):
        data = data + vk_api.groups.getMembers(group_id=GROUP_ID, v=API_VERSION,
                                               offset=i * 1000)["items"]
    data_frame = pd.read_csv(file_path, delimiter=",", encoding='utf-8')
    data_frame[COLUMN_NAME_STATUS] = ""
    data_frame[COLUMN_NAME_ERROR_MSG] = ""
    for idx, row in tqdm(data_frame.iterrows(), total=len(data_frame.index),
                         desc="Users processing"):
        col_id = row[COLUMN_NAME_VK_ID]
        book_number = row[COLUMN_NAME_BOOKNUMBER]
        logger.info(f"start processing file-id: '{col_id}'")
        if len(data_frame[(data_frame[COLUMN_NAME_BOOKNUMBER] == book_number) &
                          (data_frame[COLUMN_NAME_STATUS] != '')].index) > 0:
            data_frame.at[idx, COLUMN_NAME_STATUS] = STATUS_DUPLICATE
            logger.info(f"file-id: '{col_id}'. Found duplicate")
            continue
        try:
            valid_id = get_user_id(vk_api, col_id)
        except Exception as err:
            data_frame.at[idx, COLUMN_NAME_ERROR_MSG] = err
            data_frame.at[idx, COLUMN_NAME_STATUS] = STATUS_ERROR
            logger.exception(f"file-id: '{col_id}'. Error")
            continue
        if valid_id in data:
            data_frame.at[idx, COLUMN_NAME_STATUS] = STATUS_GROUP_MEMBER
            logger.info(f"file-id: '{col_id}'. Set status '{STATUS_GROUP_MEMBER}'")
        else:
            data_frame.at[idx, COLUMN_NAME_STATUS] = STATUS_NOT_MEMBER
            logger.info(f"file-id: '{col_id}'. Set status '{STATUS_NOT_MEMBER}'")
    data_frame.to_csv(result_path, sep=",", header=True, index=False,
                      encoding='utf-8', quoting=csv.QUOTE_MINIMAL,
                      quotechar='"')
    res_path = Path(result_path).resolve()
    logger.info(f"End processing. Save file to {res_path}")
    print(f'Result file was saved to {res_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str,
                        help="file path to processing")
    parser.add_argument("-o", "--output", type=str, default="result.csv",
                        help="file path to result csv file")
    args = parser.parse_args()
    main(args.file, args.output)

import pandas as pd
import os

def export_internal_excel(data_json):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, "workspace", "outputs")

    items = data_json['items']
    df = pd.DataFrame(items)

    df['Ten_Khach'] = data_json['khach_hang']['ten']
    df['Ngay'] = data_json['khach_hang']['ngay_bao_gia']

    file_name = f"INTERNAL_DATA_{data_json['khach_hang']['ten'].replace(' ', '_')}.xlsx"
    final_path = os.path.join(output_path, file_name)

    df.to_excel(final_path, index=False)
    return final_path
import pandas as pd
import io

def export_raw_excel(data_json):
    df = pd.DataFrame(data_json['items'])
    df['Ten_Khach'] = data_json['khach_hang']['ten']
    df['Ngay'] = data_json['khach_hang']['ngay_bao_gia']

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    return output.getvalue()
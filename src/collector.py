import requests
import pandas as pd
import os
import re
import time


def fetch_and_integrate_all():
    url = "https://mcp-api.op.gg/mcp"
    headers = {"Content-Type": "application/json"}

    # 1. 포지션 매핑 (API 요청 키 : 서버 응답 클래스 이름)
    positions = {
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "MID": "Mid",
        "ADC": "Adc",
        "SUPPORT": "Support"
    }

    all_rows = []

    print("🚀 [전 챔피언 데이터 통합 수집 시작]")

    for pos_key, class_name in positions.items():
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "lol_list_lane_meta_champions",  #
                "arguments": {
                    "region": "kr",
                    "game_mode": "ranked",
                    "position": pos_key
                }
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            res_json = response.json()

            # 응답 텍스트 추출
            raw_text = res_json['result']['content'][0]['text']

            # 2. 정규표현식으로 커스텀 데이터 파싱
            # 인덱스 가이드: 0:이름, 5:승률, 6:픽률, 8:밴률, 9:KDA, 10:티어
            pattern = rf'{class_name}\("(.*?)",.*?,.*?,.*?,.*?,([\d.]+),([\d.]+),.*?,([\d.]+),([\d.]+),(\d+)'
            matches = re.findall(pattern, raw_text)

            for m in matches:
                all_rows.append({
                    "champion": m[0],
                    "position": pos_key,
                    "win_rate": float(m[1]) * 100,
                    "pick_rate": float(m[2]) * 100,
                    "ban_rate": float(m[3]) * 100,
                    "kda": float(m[4]),
                    "tier": int(m[5])
                })

            print(f"✅ {pos_key} 데이터 처리 완료 ({len(matches)}명)")
            time.sleep(0.5)  # 서버 부하 방지 매너 타임

        except Exception as e:
            print(f"❌ {pos_key} 수집 중 오류 발생: {e}")

    # 3. 데이터 통합 및 CSV 저장
    if all_rows:
        df = pd.DataFrame(all_rows)
        # 가독성을 위해 포지션과 티어 순으로 정렬
        df = df.sort_values(by=['position', 'tier', 'win_rate'], ascending=[True, True, False])

        output_path = 'data/all_champions_meta.csv'
        os.makedirs('data', exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print("\n" + "=" * 50)
        print(f"🏆 [통합 성공] 총 {len(df)}개의 챔피언 데이터가 통합되었습니다.")
        print(f"📍 저장 위치: {output_path}")
        print("=" * 50)
    else:
        print("❌ 수집된 데이터가 없습니다. 원본 로그 형식을 다시 점검해야 합니다.")


if __name__ == "__main__":
    fetch_and_integrate_all()
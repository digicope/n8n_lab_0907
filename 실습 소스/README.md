#### 실습 소스
<br>

#### Upstage API 인증 URL :
```
Solar url : https://api.upstage.ai/v1/solar
Document OCR url : https://api.upstage.ai/v1/document-digitization
```

<br>

#### Google RSS 피드 주소 : 주식뉴스
``` https://news.google.com/rss/search?q=%EC%A3%BC%EC%8B%9D&hl=ko&gl=KR&ceid=KR%3Ako ```
<br>

```
{{ $today.format("DD") }}의 뉴스
```
<br>


```
오늘의 뉴스요약
===================
{{ $json.data.map(item => `${item.title}\n${item.link}`).join('\n\n') }}
```
<br>

#### Discord Parameters의 Message 설정 :
```
{{ $json.dt.toDateTime('s').format('yyyy-MM-dd HH:mm') }} 기준 날씨 리포트

📍 현재 서울 날씨
- 상태: {{ $json.weather[0].description }}
- 기온: {{ $json.main.temp }}°C (체감 {{ $json.main.feels_like }}°C)
- 일출: {{ $json.sys.sunrise.toDateTime('s').format('HH:mm') }} / 일몰: {{ $json.sys.sunset.toDateTime('s').format('HH:mm') }}

🌥️ 내일 예보 (오전 6시)
- 상태: {{ $json.list[8].weather[0].description }}
- 기온: {{ $json.list[8].main.temp }}°C (체감 {{ $json.list[8].main.feels_like }}°C)
```

<br>

#### 장바구니 AI Agent Description :
```
Google Sheets에서 찾은 부류코드
예: 딸기면 200, 고구마면 100 처럼  "숫자 + 00"의 형태
```
<br>

#### 장바구니 AI Agent System Message :
```
너는 사용자의 질문에 따라 KAMIS api를 이용하여 현재 농수산물에 대한 정보를 알려 주는 장바구니 AI Agent야.
사용자의 농수산품 질문에 따라 구글 시트에서 적절한 코드를 찾고 이를 이용하여 현재 가격과 최근 가격의 추이를 정리해 줘.

요즘, 최근이라고 하면 {{ $now }} 날짜 기준으로 하루 전 데이터를 조회해.
```

### import cURL
```
curl -X GET "http://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&p_product_cls_code=02&p_country_code=1101&p_regday=2015-10-01&p_convert_kg_yn=N&p_item_category_code=200&p_cert_key=111&p_cert_id=222&p_returntype=xml"
```

### 웹브라우저에서 KAMIS GET 요청 테스트 :
```
https://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&p_product_cls_code=02&p_country_code=1101&p_regday=2026-07-22&p_item_category_code=200&p_cert_key=______&p_cert_id=____&p_returntype=json
```

### 명령창에서 KAMIS GET 요청 테스트(Windows) :
```
curl -X GET "https://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&p_product_cls_code=02&p_country_code=1101&p_regday=2026-07-22&p_item_category_code=200&p_cert_key=_____&p_cert_id=____&p_returntype=json" -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" -H "Accept: application/json, text/plain, */*" -H "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8" -H "Referer: https://www.kamis.or.kr/" -H "Origin: https://www.kamis.or.kr" -H "Cache-Control: no-cache"
```
### 명령창에서 KAMIS GET 요청 테스트(MAC용) :
```
curl -X GET "https://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&p_product_cls_code=02&p_country_code=1101&p_regday=2026-07-22&p_item_category_code=200&p_cert_key=YOUR_CERT_KEY&p_cert_id=YOUR_CERT_ID&p_returntype=json" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" -H "Accept: application/json, text/plain, */*" -H "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8" -H "Referer: https://www.kamis.or.kr/" -H "Origin: https://www.kamis.or.kr" -H "Cache-Control: no-cache"
```

### 명령창에서 KAMIS GET 요청 테스트(리눅스용) :
```
curl -X GET "https://www.kamis.or.kr/service/price/xml.do?action=dailyPriceByCategoryList&p_product_cls_code=02&p_country_code=1101&p_regday=2026-07-22&p_item_category_code=200&p_cert_key=YOUR_CERT_KEY&p_cert_id=YOUR_CERT_ID&p_returntype=json" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" -H "Accept: application/json, text/plain, */*" -H "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8" -H "Referer: https://www.kamis.or.kr/" -H "Origin: https://www.kamis.or.kr" -H "Cache-Control: no-cache"
```


#### AI 영수증 정리봇 System Message :
```
3가지를 정제해

1. 구매 날짜(시분초)
2. 카드번호
3. 총금액
```
<br>

### JSON Example :
```
{
    "timestamp": "YYYY-MM-DD HH:MM:SS",
	"amt": "총 금액",
	"card": "카드번호"
}
```
<br>

### 주식 시세 — AI 투자 리포트 메일링
<br>

#### Gemini 입력 프롬프트 -1 (지수시세정보) :
```
n8n의 HTTP Request 노드를 이용해 코스피지수를 가져올 거야.
첨부된 자료를 이용해서 코스피지수를 가져오기 위한 HTTP 요청 정보를 cURL 형식으로 만들어 줘.
```
<br>

```
curl -X GET "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex?serviceKey=YOUR_SERVICE_KEY&numOfRows=1&pageNo=1&resultType=json&idxNm=%EC%BD%94%EC%8A%A4%ED%94%BC"
```

#### Gemini 입력 프롬프트 -2(주식시세정보) :
```
n8n의 HTTP Request 노드를 이용해 주식 종목 가격을 가져올 거야.
종목명은 {{$json.name}}에 있어. 첨부된 자료를 이용해서 종목 가격을 가져오기 위한 http 요청을 cURL 형식으로 만들어줘.
```
<br>

```
curl -X GET "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo?serviceKey=YOUR_SERVICE_KEY&numOfRows=1&pageNo=1&resultType=json&itmsNm={{$json.name}}"
```
<br>

#### Prompt(User Message)
```
당신은 대한민국 최고의 주식 투자 전략가입니다. 아래 제공되는 오늘의 시장 데이터를 분석하여 투자 리포트를 작성해 주세요.

## 시장 데이터

{{ $json.data }}

## 작성 지침:
1. **시장 총평**: 코스피 지수의 움직임을 바탕으로 오늘 시장의 전반적인 분위기를 한 문장으로 요약하세요.
2. **종목별 분석**: 관심 종목(삼성전자, SK하이닉스 등) 각각에 대해 현재 상태와 간단한 기술적 의견을 제시하세요.
3. **투자 전략**: 위 데이터를 종합해 볼 때, 내일 시장에서 주의 깊게 봐야 할 포인트나 대응 전략을 전문가답게 조언해 주세요.
4. **말투**: 신뢰감 있고 전문적인 어조(~입니다, ~할 것으로 보입니다)를 사용하세요.
5. **주의**: HTML 태그를 쓰지 말고 순수 텍스트로만 답변하세요. (줄바꿈은 사용 가능)
```
<br>

#### Upstage API URL :

```
Solar url : https://api.upstage.ai/v1/solar
Document OCR url : https://api.upstage.ai/v1/document-digitization
```

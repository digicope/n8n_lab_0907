### 최고의 n8n AI자동화 강의 : 실습 답안
<br>



#### Gmail
Subject
```
[n8nKorea] {{$now.format('yyyy-MM-dd')}} 일자 매체별 광고비를 발송 드립니다.
```
<br>
Message
```
{{$now.format('yyyy-MM-dd')}} 일자 매체별 광고비 데이터 입니다.

네이버 : {{ $('Google Sheets').item.json['네이버'] }} 원
카카오 : {{ $('Google Sheets').item.json['카카오'] }} 원
구글 : {{ $('Google Sheets').item.json['구글'] }} 원
페이스북 : {{ $('Google Sheets').item.json['페이스북'] }} 원
인스타그램 : {{ $('Google Sheets').item.json['인스타그램'] }} 원

시각 자료는 첨부파일을 확인해주세요
```




# 四六级考号查询
------


## 部署运行
```bash
pip install -r requirements.txt
python serve.py # 映射端口为 8888
```

## docker部署运行
```bash
docker-compose up --scale app=3 -d # 映射端口为 50000
```
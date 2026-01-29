가상환경 설치 (처음한번만):
conda create -n myenv python=3.11 -y
conda activate myenv
pip install -r requirements.txt

실행:
conda activate myenv
python app.py
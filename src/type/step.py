import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

class StepAnalyzer:
    def __init__(self, df=None, csv_file="dammy_step_data.csv"):
        if df is not None:
            self.df = df
        else:
            self.df = pd.read_csv(csv_file)
    
    def get_day_type(self, date=None):
        """日付から曜日タイプを取得"""
        if date is None:
            date = datetime.now(ZoneInfo("Asia/Tokyo"))
        
        weekday = date.weekday()
        day_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday","holiday"]
        return day_map[weekday]
    
    def analyze_today(self, date=None):
        """今日の曜日データを分析"""
        day_type = self.get_day_type(date)
        
        # データベース形式の場合は日付から曜日を計算
        if 'analysis_date' in self.df.columns:
            self.df['day_type'] = pd.to_datetime(self.df['analysis_date']).dt.day_name()
            today_data = self.df[self.df['day_type'] == day_type.replace('Monday', 'Monday').replace('Tuesday', 'Tuesday').replace('Wednesday', 'Wednesday').replace('Thursday', 'Thursday').replace('Friday', 'Friday').replace('Saturday', 'Saturday').replace('Sunday', 'Sunday')]
            steps_col = 'final_steps'
        else:
            today_data = self.df[self.df['day_type'] == day_type]
            steps_col = 'steps'
        
        if today_data.empty:
            return {
                'day_type': day_type,
                'count': 0,
                'avg_steps': 0,
                'predicted_steps': 8000
            }
        
        avg_steps = int(today_data[steps_col].mean())
        
        return {
            'day_type': day_type,
            'count': len(today_data),
            'avg_steps': avg_steps,
            'predicted_steps': avg_steps
        }

if __name__ == "__main__":
    analyzer = StepAnalyzer()
    
    # 今日の分析
    result = analyzer.analyze_today()
    
    print(f"今日の曜日: {result['day_type']}")
    print(f"過去データ数: {result['count']}件")
    print(f"平均歩数: {result['avg_steps']:,}歩")
    print(f"予測歩数: {result['predicted_steps']:,}歩")
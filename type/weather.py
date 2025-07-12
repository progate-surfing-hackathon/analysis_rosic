import requests
from datetime import datetime

class MeteoWeatherAPI:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
    
    def get_coordinates(self, location):
        """地名から緯度経度を取得"""
        try:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": location, "count": 1, "language": "en", "format": "json"}
            
            response = requests.get(geo_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("results"):
                return None, None
            
            result = data["results"][0]
            return result["latitude"], result["longitude"]
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None, None
    
    def get_historical_weather(self, lat, lon, date_str):
        """過去の天気データを取得"""
        try:
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": date_str,
                "end_date": date_str,
                "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,relative_humidity_2m_mean,surface_pressure_mean",
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_weather_summary(self, location, date_str):
        """指定地域・日付の天気サマリーを取得"""
        try:
            lat, lon = self.get_coordinates(location)
            if lat is None:
                return None
            
            data = self.get_historical_weather(lat, lon, date_str)
            if not data or "daily" not in data:
                return None
            
            daily = data["daily"]
            
            return {
                "date": date_str,
                "location": location,
                "temp_min": daily["temperature_2m_min"][0],
                "temp_max": daily["temperature_2m_max"][0],
                "temp_avg": daily["temperature_2m_mean"][0],
                "humidity_avg": daily["relative_humidity_2m_mean"][0],
                "pressure_avg": daily["surface_pressure_mean"][0]
            }
            
        except Exception as e:
            print(f"Weather summary error: {e}")
            return None

if __name__ == "__main__":
    weather = MeteoWeatherAPI()
    
    result = weather.get_weather_summary("Tokyo", "2024-12-15")
    if result:
        print(f"平均気温: {result['temp_avg']:.1f}℃")
    else:
        print("天気データの取得に失敗しました")
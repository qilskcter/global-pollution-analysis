import requests

API_KEY = "a8c35a6b54ef7bbf688768bb545ee920" #

def get_realtime_data(city_name):
    """Lấy dữ liệu Geo và Air Pollution từ OpenWeatherMap."""
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
        geo = requests.get(geo_url).json()
        if not geo:
            return None, "Không tìm thấy thành phố này."
        
        lat, lon = geo[0]['lat'], geo[0]['lon']
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        res = requests.get(aqi_url).json()
        
        return {
            "name": geo[0]['name'],
            "country": geo[0]['country'],
            "components": res['list'][0]['components']
        }, None
    except Exception as e:
        return None, f"Lỗi kết nối: {str(e)}"
import numpy as np
from sklearn import sklearn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

data = np.loadtxt("Bank_Customer.csv", skiprows=1, dtype=str, delimiter=",")

'''
Your work
非數值型資料需轉換成數值型資料 (country, gender)
去除掉無意義的特徵類別 (customer_id)
標準化特徵 (StandardScaler)
'''
# 1. 去除無意義特徵 customer_id (第 0 欄)，並將類別欄位轉為數值
# country (第 2 欄) 屬於無序名目資料，採 One-Hot Encoding 拆為 3 個 0/1 欄位
is_france = (data[:, 2] == "France").astype(float)
is_germany = (data[:, 2] == "Germany").astype(float)
is_spain = (data[:, 2] == "Spain").astype(float)

# gender (第 3 欄) 為二元類別，轉為 Female=0, Male=1
gender = (data[:, 3] == "Male").astype(float)

# 2. 組合所有數值型特徵：credit_score(1), country(One-Hot), gender, age~estimated_salary(4~10)
features = np.column_stack((
    data[:, 1].astype(float),
    is_france,
    is_germany,
    is_spain,
    gender,
    data[:, 4:-1].astype(float),
))

# 3. 使用 StandardScaler 對特徵進行標準化 (目標標籤 churn 不標準化)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# 目標標籤 churn (最後一欄，轉為整數 0/1)
labels = data[:, -1].astype(int)

# 組合前處理後的完整資料並存檔
pre_data = np.column_stack((features_scaled, labels))
np.savetxt("Bank_Customer_Preprocessed.csv", pre_data, delimiter=",")


from sklearn.linear_model import LogisticRegression
# 決策分類器
clf = LogisticRegression()

'''
Your work
切割 data 為 x_train, x_test, y_train, y_test
請學習 train_test_split 的使用方法
'''
# 將特徵與標籤依 80% 訓練集 / 20% 測試集進行切割
x = pre_data[:, :-1]
y = pre_data[:, -1].astype(int)
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42
)

# 使用訓練集來訓練我們的分類器
clf.fit(x_train, y_train)
# 測試資料集中進行預測
pred = clf.predict(x_test)

#print (pred) # 預測分類，即客戶是否流失
#print (y_test) # 分類
print (str(accuracy_score(pred, y_test)*100 ) + "% ")   # 預測精度

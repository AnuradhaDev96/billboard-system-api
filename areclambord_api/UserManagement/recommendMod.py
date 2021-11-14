import numpy as np
import pandas as pd
from ast import literal_eval as make_tuple
from tensorflow import keras
from tensorflow.keras.optimizers import Adam

from UserManagement.enums import BillboardType

records = pd.read_csv("inferenceset.csv")
# ANNmodel = pickle.load(open('ANN.h5', 'rb'))
ANNmodel = keras.models.load_model('ANN.h5')


# @api_view(['POST'])
# def eval_progress(request):
#     evaluate_data = JSONParser().parse(request)
#     suggestion = inputprepare(records, evaluate_data.get("billboardCategory"), evaluate_data.get("latitude"),
#                               evaluate_data.get("longitude"))
#     return JsonResponse({'message': suggestion}, status=status.HTTP_400_BAD_REQUEST)


def inputprepare(df, billboardcat, billat, billong):
    inputdata = pd.DataFrame()
    inputdata['Mature'] = df['IDNo'].apply(lambda x: 1 if 85 < int(str(x)[:2]) < 95 else 0)
    inputdata['Middle'] = df['IDNo'].apply(lambda x: 1 if 61 < int(str(x)[:2]) < 85 else 0)
    inputdata['Old'] = df['IDNo'].apply(lambda x: 1 if 41 < int(str(x)[:2]) < 61 else 0)
    inputdata['Young or Teen'] = df['IDNo'].apply(
        lambda x: 1 if not (85 < int(str(x)[:2]) < 95 or 61 < int(str(x)[:2]) < 85 or 41 < int(str(x)[:2]) < 61) else 0)
    inputdata['startlat'] = df['Start'].apply(lambda x: make_tuple(x)[0])
    inputdata['startlong'] = df['Start'].apply(lambda x: make_tuple(x)[1])
    inputdata['point1_lat'] = df['RandomPoint1'].apply(lambda x: make_tuple(x)[0])
    inputdata['point1_long'] = df['RandomPoint1'].apply(lambda x: make_tuple(x)[1])
    inputdata['point2_lat'] = df['RandomPoint2'].apply(lambda x: make_tuple(x)[0])
    inputdata['point2_long'] = df['RandomPoint2'].apply(lambda x: make_tuple(x)[1])
    inputdata['endlat'] = df['End'].apply(lambda x: make_tuple(x)[0])
    inputdata['endlong'] = df['End'].apply(lambda x: make_tuple(x)[1])
    inputdata['billlat'] = billat
    inputdata['billlong'] = billong
    inputdata['billMature'] = 1 if billboardcat == BillboardType.MEDIUM.value else 0
    inputdata['billMiddle'] = 1 if billboardcat == BillboardType.LARGE.value else 0
    inputdata['billOld'] = 1 if billboardcat == BillboardType.DIGITAL.value else 0
    inputdata['billYoung or teen'] = 1 if billboardcat == BillboardType.SMALL.value else 0
    inputdata = inputdata.round(
        {"startlat": 4, "startlong": 4, "point1_lat": 4, "point1_long": 4, "point2_lat": 4, "point2_long": 4,
         "endlat": 4, "endlong": 4, "billlat": 4, "billlong": 4})
    predictions = ANNmodel.predict(inputdata)
    predictions = (predictions > 0.5).astype(np.float32)
    predictions = predictions.reshape(-1, )
    targetscovered = predictions.shape[0] - np.count_nonzero(predictions == 0)
    print(targetscovered)
    if targetscovered <= 1000:
        # remove the billboard
        return "REMOVE"

    elif 1000 < targetscovered <= 3000:
        # Buy Silver Subscription
        return "CHANGE_SUBSCRIPTION"

    else:
        # Buy Gold Subscription
        return "MAINTAIN"


prediction = inputprepare(records, BillboardType.DIGITAL.value, 6.8997, 79.9453)

print(BillboardType.DIGITAL.value)
print(prediction)

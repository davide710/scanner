import cv2
import numpy as np
import pandas as pd

imlist = ['ex_doc.jpg', 'prova1.jpeg', 'prova2.jpeg', 'prova3.jpeg', 'prova4.jpeg', 'prova5.jpeg']

for path in imlist:
    im = cv2.imread(f'examples/test_images/{path}')

    if False:
        scale_factor = 0.3
        width = int(im.shape[1] * scale_factor)
        height = int(im.shape[0] * scale_factor)
        dimension = (width, height)
        im = cv2.resize(im, dimension, interpolation = cv2.INTER_AREA)

    im = np.array(im)

    df = np.reshape(im, (-1, 3))
    df = pd.DataFrame(df, columns=['B', 'G', 'R'])
    df['stdev'] = np.std(df, axis=1)
    #print(df.head(10))
    #print(df.describe())
    #print(df.stdev.value_counts())
    #print(im.shape)
    #print(df.shape)
    #print(df.loc[df.stdev < 5].count())
    df['meann'] = np.mean(df, axis=1)

    #df.loc[(df.stdev < 400) & (df.meann > 0)].B = 0 
    #df.loc[(df.stdev < 400) & (df.meann > 0)].G = 0
    #df.loc[(df.stdev < 400) & (df.meann > 0)].R = 0
    df.B = np.where(((df.stdev < 10) & (df.meann > 90)), 255, df.B)
    df.G = np.where(((df.stdev < 10) & (df.meann > 90)), 255, df.G)
    df.R = np.where(((df.stdev < 10) & (df.meann > 90)), 255, df.R)

    df.drop(['stdev', 'meann'], axis=1, inplace=True)
    print(df.head())
    print(df.shape)
    new = np.array(df)
    print(new.shape)
    new = np.reshape(new, (im.shape[0], im.shape[1], 3))

    cv2.imshow('orig', im)
    cv2.imshow('new', new)
    cv2.waitKey(0)
    cv2.imwrite(f'examples/test_images/whited_{path}', new)

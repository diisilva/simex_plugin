import ee
ee.Initialize()

def cloudScoreMask(image):
    
    cloudThresh = 15

    score = ee.Image(1.0)

    # Clouds are reasonably bright in the blue band.
    blue = image.select('blue')
    score = score.min(rescale(blue, min=1000, max=3000))

    # Clouds are reasonably bright in all visible bands.
    visibleSum = image.expression("b('red') + b('green') + b('blue')")
    score = score.min(rescale(visibleSum, min=2000, max=8000))

    # Clouds are reasonably bright in all infrared bands.
    infraredSum = image.expression("b('nir') + b('swir1') + b('swir2')")
    score = score.min(rescale(infraredSum, min=3000, max=8000))

    # temperature = image.select('temp') # Sentinel 2 images doesn't have thermal band

    # However, clouds are not snow.
    ndsi = image.normalizedDifference(['green', 'swir1'])
    score = score.min(rescale(ndsi, min=8000, max=6000))

    # reescale score
    score = score.multiply(100).byte()
    score = score.gte(cloudThresh).rename('cloudScoreMask')

    return image.addBands(score)


# In[4]:


def maskQA60(image):
  
  bandQA60 = image.select(['QA60']).neq(0)
  bandQA60 = bandQA60.mask(bandQA60).rename(['maskQA60'])
#   imageMask = imageCclouds.rename(['maskQA60'])
  
  return image.addBands(bandQA60)


# In[5]:


def tdom(collection,
         zScoreThresh=-1,
         shadowSumThresh=5000,
         dilatePixels=2):

    shadowSumBands = ['nir', 'swir1']

    irStdDev = collection         .select(shadowSumBands)         .reduce(ee.Reducer.stdDev())

    irMean = collection         .select(shadowSumBands)         .mean()

    def _maskDarkOutliers(image):
        zScore = image.select(shadowSumBands)             .subtract(irMean)             .divide(irStdDev)

        irSum = image.select(shadowSumBands)             .reduce(ee.Reducer.sum())

        tdomMask = zScore.lt(zScoreThresh)             .reduce(ee.Reducer.sum())             .eq(2)             .And(irSum.lt(shadowSumThresh)) 
        tdomMask = tdomMask.focal_min(dilatePixels)

        return image.addBands(tdomMask.rename('tdomMask'))

    collection = collection.map(_maskDarkOutliers)

    return collection


# In[6]:


def cloudProject(image,
                 cloudBand=None,
                 shadowSumThresh=5000,
                 cloudHeights=[],
                 dilatePixels=2):

    cloud = image.select(cloudBand)

    # Get TDOM mask
    tdomMask = image.select(['tdomMask'])

    darkPixels = image.select(['nir', 'swir1', 'swir2'])         .reduce(ee.Reducer.sum())         .lt(shadowSumThresh)

    nominalScale = cloud.projection().nominalScale()

    meanAzimuth = image.get('sun_azimuth_angle')
    meanElevation = image.get('sun_elevation_angle')

    azR = ee.Number(meanAzimuth)         .multiply(math.pi)         .divide(180.0)         .add(ee.Number(0.5).multiply(math.pi))

    zenR = ee.Number(0.5)         .multiply(math.pi)         .subtract(ee.Number(meanElevation).multiply(math.pi).divide(180.0))

    def _findShadow(cloudHeight):
        cloudHeight = ee.Number(cloudHeight)

        shadowCastedDistance = zenR.tan()             .multiply(cloudHeight)

        x = azR.cos().multiply(shadowCastedDistance)             .divide(nominalScale).round()

        y = azR.sin().multiply(shadowCastedDistance)             .divide(nominalScale).round()

        return cloud.changeProj(cloud.projection(), cloud.projection().translate(x, y))

    shadows = cloudHeights.map(_findShadow)

    shadow = ee.ImageCollection.fromImages(shadows).max().unmask()
    shadow = shadow.focal_max(dilatePixels)
    shadow = shadow.And(darkPixels).And(tdomMask.Not().And(cloud.Not()))

    shadowMask = shadow.rename(['cloudShadowTdomMask'])

    return image.addBands(shadowMask)


# In[7]:


def cloudFlagMaskToaLX(image):

    qaBand = image.select('QA60')

    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 5))).neq(0)         .Or(qaBand.bitwiseAnd(int(math.pow(2, 6))).neq(0))         .rename('cloudFlagMask')

    return ee.Image(cloudMask)


# In[8]:


def cloudFlagMaskToaS2(image):

    qaBand = image.select('QA60')

    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 10))).neq(0)         .Or(qaBand.bitwiseAnd(int(math.pow(2, 11))).neq(0))         .rename('cloudFlagMask')

    return ee.Image(cloudMask)


# In[9]:


def cloudFlagMaskToa(image):

    isSentinel = ee.String(image.get('satellite_name'))         .slice(0, 10).compareTo('Sentinel-2').Not()

    cloudMask = ee.Algorithms.If(
        isSentinel,
        cloudFlagMaskToaS2(image),
        cloudFlagMaskToaLX(image))

    return ee.Image(cloudMask)


# In[10]:


def maskCloudFraction(image):
  
  cloudFraction = image.select(['cloud'])
  
  imageNcloudFraction = image.updateMask(cloudFraction.lte(20))
  
  return imageNcloudFraction


# In[12]:


def calculusCloud(obj):
  
#   bandQA60 = obj['image'].select('QA60').neq(0)
#   imageClouds = bandQA60.mask(bandQA60).clip(obj['geoGleba'])
  reducer = obj['imageMask'].And(obj['image']).select('blue').rename('mask').reduceRegion(ee.Reducer.sum(),obj['geoGleba'],20)
  areaClouds = ee.Number(reducer.get('mask')).multiply(10*10).divide(10000)
  percentCloud = areaClouds.divide(obj['areaGleba']).multiply(100)
  
  return obj['image'].set('cloud_fraction', percentCloud)
  


# In[13]:


def masksAll(obj):

    masks = obj['image'].select([
            #'cloudShadowTdomMask',
              'cloudScoreMask',
              'tdomMask'
             ]).reduce(ee.Reducer.anyNonZero())
    
    
    obj['imageMask'] = obj['image'].mask(masks.eq(1))



    image = calculusCloud(obj)

    return image


# In[14]:


def cloudFlagMaskSr(image):

    qaBand = image.select('QA60')

    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 5)))         .neq(0)         .rename('cloudFlagMask')

    return ee.Image(cloudMask)


# In[15]:


def cloudFlagMask(image):

    isToa = ee.String(image.get('reflectance')).compareTo('TOA').Not()

    cloudMask = ee.Algorithms.If(
        isToa,
        cloudFlagMaskToa(image),
        cloudFlagMaskSr(image))

    return image.addBands(ee.Image(cloudMask))


# In[16]:


def cloudShadowFlagMaskToaLX(image):

    qaBand = image.select('QA60')

    cloudShadowMask = qaBand.bitwiseAnd(int(math.pow(2, 7))).neq(0)         .Or(qaBand.bitwiseAnd(int(math.pow(2, 8))).neq(0))         .rename('cloudShadowFlagMask')

    return ee.Image(cloudShadowMask)


# In[17]:


def cloudShadowFlagMaskSrLX(image):

    qaBand = image.select('QA60')

    cloudMask = qaBand.bitwiseAnd(int(math.pow(2, 5)))         .neq(0)         .rename('cloudShadowFlagMask')

    return ee.Image(cloudMask)


# In[18]:


def cloudShadowFlagMask(image):

    isSentinel = ee.String(image.get('satellite_name'))         .slice(0, 10).compareTo('Sentinel-2').Not()

    isToa = ee.String(image.get('reflectance')).compareTo('TOA').Not()

    cloudShadowMask = ee.Algorithms.If(
        isSentinel,
        ee.Image(0).mask(image.select(0)).rename('cloudShadowFlagMask'),
        ee.Algorithms.If(
            isToa,
            cloudShadowFlagMaskToaLX(image),
            cloudShadowFlagMaskSrLX(image)))

    return image.addBands(ee.Image(cloudShadowMask))


# In[19]:


def getMasks(collection,
             zScoreThresh=-1,
             shadowSumThresh=5000,
             dilatePixels=1,
             cloudFlag=True,
             cloudScore=True,
             cloudShadowFlag=True,
             cloudShadowTdom=True,
             cloudHeights=[],
             cloudBand=None):

    collection = ee.Algorithms.If(
        cloudFlag,
        ee.Algorithms.If(
            cloudScore,
            collection.map(cloudFlagMask).map(cloudScoreMask),
            collection.map(cloudFlagMask)),
        collection.map(cloudScoreMask))

    collection = ee.ImageCollection(collection)

    collection = ee.Algorithms.If(
        cloudShadowFlag,
        ee.Algorithms.If(
            cloudShadowTdom,
            tdom(collection.map(cloudShadowFlagMask),
                 zScoreThresh=zScoreThresh,
                 shadowSumThresh=shadowSumThresh,
                 dilatePixels=dilatePixels),
            collection.map(cloudShadowFlagMask)),
        tdom(collection,
             zScoreThresh=zScoreThresh,
             shadowSumThresh=shadowSumThresh,
             dilatePixels=dilatePixels))

    collection = ee.ImageCollection(collection)

    def _getShadowMask(image):

        image = cloudProject(image,
                             shadowSumThresh=shadowSumThresh,
                             dilatePixels=dilatePixels,
                             cloudHeights=cloudHeights,
                             cloudBand=cloudBand)

        return image

    collection = collection.map(_getShadowMask)

    return collection


# In[20]:


def getCloudAOI(obj):
  
  
  image = calculusCloud(obj)
  
  return image


# In[21]:


def setProperties(image):
     
           cloudCover = ee.Algorithms.If(image.get('CLOUD_COVER'),                   image.get('CLOUD_COVER'),                   image.get('CLOUDY_PIXEL_PERCENTAGE'))
               
           date = ee.Algorithms.If(image.get('DATE_ACQUIRED'),image.get('DATE_ACQUIRED'),ee.Algorithms.If(image.get('SENSING_TIME'),image.get('SENSING_TIME'),image.get('GENERATION_TIME')))
           
           satellite = ee.Algorithms.If(image.get('SPACECRAFT_ID'),                   image.get('SPACECRAFT_ID'),                   ee.Algorithms.If(image.get('SATELLITE'),                       image.get('SATELLITE'),                       image.get('SPACECRAFT_NAME')                   )               )
           
           azimuth = ee.Algorithms.If(image.get('SUN_AZIMUTH'),                   image.get('SUN_AZIMUTH'),                   ee.Algorithms.If(image.get('SOLAR_AZIMUTH_\ANGLE'),                       image.get('SOLAR_AZIMUTH_ANGLE'),
                       image.get('MEAN_SOLAR_AZIMUTH_ANGLE')\
                   )\
               )
           
           elevation = ee.Algorithms.If(image.get('SUN_ELEVATION'),                   image.get('SUN_ELEVATION'),                   ee.Algorithms.If(image.get('SOLAR_ZENITH_ANGLE'),                       ee.Number(90).subtract(image.get('SOLAR_ZENITH_ANGLE')),                       ee.Number(90).subtract(image.get('MEAN_SOLAR_ZENITH_ANGLE'))                   )               )
           
           reflectance = ee.Algorithms.If(
                   ee.String(ee.Dictionary(ee.Algorithms.Describe(image)).get('id')).match('SR').length(),\
                   'SR',\
                   'TOA'\
               )
           
           return image                   .set('cloud_cover', cloudCover)                   .set('satellite_name', satellite)                   .set('sun_azimuth_angle', azimuth)                   .set('sun_elevation_angle', elevation)                   .set('reflectance', reflectance)                   .set('date', ee.Date(date).format('Y-MM-dd'))


# In[22]:


def getCollection(obj):
    
            collection = ee.ImageCollection(obj['collectionid']).filterBounds(obj['geometry']).filterDate(ee.Date(obj['dateStart']),ee.Date(obj['dateEnd'])).map(setProperties)
      
            collection = collection.filterMetadata('cloud_cover','less_than',obj['cloud_cover'])

            return collection


# In[23]:


def getSMA(image):
    
            endmembers = [
                    [119.0, 475.0, 169.0, 6250.0, 2399.0, 675.0], #/*gv*/
                    [1514.0, 1597.0, 1421.0, 3053.0, 7707.0, 1975.0], #/*npv*/
                    [1799.0, 2479.0, 3158.0, 5437.0, 7707.0, 6646.0], #/*soil*/
                    [4031.0, 8714.0, 7900.0, 8989.0, 7002.0, 6607.0] #/*cloud*/
                ]
            
            bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
            outBandNames = ['gv', 'npv', 'soil', 'cloud']
            
            fractions = ee.Image(image)                            .select(bandNames)                            .unmix(endmembers)                            .max(0)                            .multiply(100)                            .byte()                        
            image = image.addBands(fractions.rename(outBandNames))

            #   // get shade and gvs
            summed = image.expression('b("gv") + b("npv") + b("soil")')

            shd = summed.subtract(100).abs().byte()
            gvs = image.select("gv")                        .divide(summed)                        .multiply(100)                        .byte()
            image = image.addBands(gvs.rename("gvs"))
            image = image.addBands(shd.rename("shade"))

            return image.copyProperties(image)
        


# In[24]:


def getNDFI(image):

  gvs = image.select("gvs")

  npvSoil = image.expression('b("npv") + b("soil")')

  ndfi = ee.Image.cat(gvs, npvSoil).normalizedDifference().rename('ndfi').float()
#   // rescale NDFI from 0 until 200
  ndfi = ndfi.expression('byte(b("ndfi") * 100 + 100)')

  return image.addBands(ndfi).copyProperties(image)


# In[27]:


def getNDVI(image):
  
  exp = "(b('nir')-b('red'))/(b('nir')+b('red'))"
  ndvi = image.expression(exp).rename("ndvi").float()
  
  return image.addBands(ndvi)


# In[26]:


def bandNames(key):
    
            bandNames = {'sentinel2' : {
                'bandNames': ['B2','B3','B4','B8','B10','B11','B12','QA60'],
                'newNames': ['blue','green','red','nir','cirrus','swir1','swir2','QA60'] },
                        'sentinel2_SR' : {
                  'bandNames': ['B2','B3','B4','B8','B11','B12','QA60'],
                  'newNames': ['blue','green','red','nir','swir1','swir2','QA60']
                }, 'l5': {
      'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
      'newNames': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa', 'temp']
  },
  
 'l7': {
      'bandNames': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa', 'B6'],
      'newNames': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa', 'temp']
  },

  'l8' : {
      'bandNames': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'pixel_qa', 'B11'],
      'newNames': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'thermal', 'pixel_qa', 'temp']
  }}
        
            return bandNames[key]


# In[ ]:

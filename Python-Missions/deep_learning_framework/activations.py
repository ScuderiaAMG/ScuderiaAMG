"""Exhaustive activation functions library."""
import numpy as np
from typing import Optional, Tuple

_EPS = 1e-8

# Pre-computed GELU approximation table (256 entries)
GELU_TABLE = np.array([
    -0.0000702459,
    -0.0000814690,
    -0.0000943226,
    -0.0001090175,
    -0.0001257882,
    -0.0001448942,
    -0.0001666232,
    -0.0001912925,
    -0.0002192521,
    -0.0002508869,
    -0.0002866195,
    -0.0003269130,
    -0.0003722736,
    -0.0004232540,
    -0.0004804561,
    -0.0005445340,
    -0.0006161977,
    -0.0006962155,
    -0.0007854182,
    -0.0008847011,
    -0.0009950285,
    -0.0011174357,
    -0.0012530328,
    -0.0014030073,
    -0.0015686271,
    -0.0017512433,
    -0.0019522922,
    -0.0021732981,
    -0.0024158749,
    -0.0026817279,
    -0.0029726550,
    -0.0032905479,
    -0.0036373921,
    -0.0040152672,
    -0.0044263462,
    -0.0048728945,
    -0.0053572680,
    -0.0058819108,
    -0.0064493517,
    -0.0070622008,
    -0.0077231441,
    -0.0084349385,
    -0.0092004048,
    -0.0100224207,
    -0.0109039117,
    -0.0118478423,
    -0.0128572049,
    -0.0139350086,
    -0.0150842661,
    -0.0163079798,
    -0.0176091272,
    -0.0189906440,
    -0.0204554073,
    -0.0220062165,
    -0.0236457740,
    -0.0253766638,
    -0.0272013299,
    -0.0291220528,
    -0.0311409253,
    -0.0332598276,
    -0.0354804005,
    -0.0378040186,
    -0.0402317625,
    -0.0427643898,
    -0.0454023059,
    -0.0481455345,
    -0.0509936868,
    -0.0539459316,
    -0.0570009644,
    -0.0601569767,
    -0.0634116263,
    -0.0667620066,
    -0.0702046177,
    -0.0737353375,
    -0.0773493945,
    -0.0810413410,
    -0.0848050284,
    -0.0886335835,
    -0.0925193874,
    -0.0964540560,
    -0.1004284230,
    -0.1044325256,
    -0.1084555927,
    -0.1124860364,
    -0.1165114472,
    -0.1205185913,
    -0.1244934132,
    -0.1284210412,
    -0.1322857970,
    -0.1360712100,
    -0.1397600351,
    -0.1433342756,
    -0.1467752102,
    -0.1500634249,
    -0.1531788491,
    -0.1561007963,
    -0.1588080094,
    -0.1612787107,
    -0.1634906558,
    -0.1654211918,
    -0.1670473195,
    -0.1683457597,
    -0.1692930227,
    -0.1698654809,
    -0.1700394448,
    -0.1697912416,
    -0.1690972952,
    -0.1679342091,
    -0.1662788500,
    -0.1641084329,
    -0.1614006056,
    -0.1581335347,
    -0.1542859902,
    -0.1498374288,
    -0.1447680769,
    -0.1390590105,
    -0.1326922331,
    -0.1256507510,
    -0.1179186442,
    -0.1094811347,
    -0.1003246493,
    -0.0904368786,
    -0.0798068304,
    -0.0684248777,
    -0.0562828014,
    -0.0433738261,
    -0.0296926507,
    -0.0152354716,
    0.0000000000,
    0.0160145284,
    0.0328073493,
    0.0503761739,
    0.0687171986,
    0.0878251223,
    0.1076931696,
    0.1283131214,
    0.1496753507,
    0.1717688653,
    0.1945813558,
    0.2180992490,
    0.2423077669,
    0.2671909895,
    0.2927319231,
    0.3189125712,
    0.3457140098,
    0.3731164653,
    0.4010993944,
    0.4296415671,
    0.4587211500,
    0.4883157909,
    0.5184027048,
    0.5489587584,
    0.5799605552,
    0.6113845191,
    0.6432069773,
    0.6754042403,
    0.7079526805,
    0.7408288082,
    0.7740093442,
    0.8074712893,
    0.8411919906,
    0.8751492037,
    0.9093211509,
    0.9436865751,
    0.9782247898,
    1.0129157244,
    1.0477399649,
    1.0826787900,
    1.1177142030,
    1.1528289588,
    1.1880065868,
    1.2232314087,
    1.2584885528,
    1.2937639636,
    1.3290444073,
    1.3643174744,
    1.3995715770,
    1.4347959440,
    1.4699806126,
    1.5051164165,
    1.5401949716,
    1.5752086590,
    1.6101506055,
    1.6450146625,
    1.6797953823,
    1.7144879934,
    1.7490883737,
    1.7835930233,
    1.8179990356,
    1.8523040684,
    1.8865063132,
    1.9206044655,
    1.9545976941,
    1.9884856102,
    2.0222682375,
    2.0559459814,
    2.0895195995,
    2.1229901724,
    2.1563590747,
    2.1896279472,
    2.2227986701,
    2.2558733362,
    2.2888542260,
    2.3217437835,
    2.3545445927,
    2.3872593560,
    2.4198908728,
    2.4524420202,
    2.4849157339,
    2.5173149914,
    2.5496427951,
    2.5819021577,
    2.6140960883,
    2.6462275793,
    2.6782995952,
    2.7103150615,
    2.7422768559,
    2.7741877992,
    2.8060506483,
    2.8378680892,
    2.8696427320,
    2.9013771055,
    2.9330736538,
    2.9647347328,
    2.9963626079,
    3.0279594521,
    3.0595273450,
    3.0910682721,
    3.1225841251,
    3.1540767019,
    3.1855477078,
    3.2169987567,
    3.2484313729,
    3.2798469927,
    3.3112469672,
    3.3426325643,
    3.3740049715,
    3.4053652989,
    3.4367145818,
    3.4680537845,
    3.4993838023,
    3.5307054660,
    3.5620195439,
    3.5933267460,
    3.6246277264,
    3.6559230870,
    3.6872133805,
    3.7184991131,
    3.7497807479,
    3.7810587075,
    3.8123333768,
    3.8436051058,
    3.8748742118,
    3.9061409825,
    3.9374056774,
    3.9686685310,
], dtype=np.float32)

# Pre-computed Swish/SiLU table (256 entries)
SILU_TABLE = np.array([
    -0.0719448398,
    -0.0736066779,
    -0.0753008947,
    -0.0770278442,
    -0.0787878692,
    -0.0805813006,
    -0.0824084562,
    -0.0842696391,
    -0.0861651372,
    -0.0880952214,
    -0.0900601446,
    -0.0920601400,
    -0.0940954198,
    -0.0961661739,
    -0.0982725679,
    -0.1004147417,
    -0.1025928076,
    -0.1048068489,
    -0.1070569175,
    -0.1093430323,
    -0.1116651771,
    -0.1140232985,
    -0.1164173037,
    -0.1188470583,
    -0.1213123839,
    -0.1238130556,
    -0.1263487996,
    -0.1289192908,
    -0.1315241497,
    -0.1341629399,
    -0.1368351652,
    -0.1395402666,
    -0.1422776195,
    -0.1450465303,
    -0.1478462333,
    -0.1506758875,
    -0.1535345732,
    -0.1564212886,
    -0.1593349462,
    -0.1622743692,
    -0.1652382880,
    -0.1682253362,
    -0.1712340471,
    -0.1742628495,
    -0.1773100642,
    -0.1803738998,
    -0.1834524486,
    -0.1865436827,
    -0.1896454501,
    -0.1927554702,
    -0.1958713303,
    -0.1989904808,
    -0.2021102319,
    -0.2052277489,
    -0.2083400485,
    -0.2114439950,
    -0.2145362960,
    -0.2176134990,
    -0.2206719872,
    -0.2237079767,
    -0.2267175121,
    -0.2296964641,
    -0.2326405255,
    -0.2355452090,
    -0.2384058440,
    -0.2412175746,
    -0.2439753569,
    -0.2466739571,
    -0.2493079504,
    -0.2518717191,
    -0.2543594522,
    -0.2567651445,
    -0.2590825966,
    -0.2613054153,
    -0.2634270144,
    -0.2654406160,
    -0.2673392522,
    -0.2691157675,
    -0.2707628218,
    -0.2722728939,
    -0.2736382857,
    -0.2748511269,
    -0.2759033805,
    -0.2767868489,
    -0.2774931806,
    -0.2780138781,
    -0.2783403057,
    -0.2784636988,
    -0.2783751735,
    -0.2780657370,
    -0.2775262988,
    -0.2767476828,
    -0.2757206398,
    -0.2744358607,
    -0.2728839908,
    -0.2710556448,
    -0.2689414214,
    -0.2665319200,
    -0.2638177570,
    -0.2607895830,
    -0.2574381006,
    -0.2537540822,
    -0.2497283887,
    -0.2453519883,
    -0.2406159756,
    -0.2355115912,
    -0.2300302409,
    -0.2241635153,
    -0.2179032096,
    -0.2112413430,
    -0.2041701781,
    -0.1966822398,
    -0.1887703344,
    -0.1804275677,
    -0.1716473632,
    -0.1624234791,
    -0.1527500250,
    -0.1426214782,
    -0.1320326984,
    -0.1209789418,
    -0.1094558748,
    -0.0974595858,
    -0.0849865965,
    -0.0720338718,
    -0.0585988283,
    -0.0446793423,
    -0.0302737553,
    -0.0153808792,
    0.0000000000,
    0.0158691208,
    0.0322262447,
    0.0490706577,
    0.0664011717,
    0.0842161282,
    0.1025134035,
    0.1212904142,
    0.1405441252,
    0.1602710582,
    0.1804673016,
    0.2011285218,
    0.2222499750,
    0.2438265209,
    0.2658526368,
    0.2883224323,
    0.3112296656,
    0.3345677602,
    0.3583298219,
    0.3825086570,
    0.4070967904,
    0.4320864847,
    0.4574697591,
    0.4832384088,
    0.5093840244,
    0.5358980117,
    0.5627716113,
    0.5899959178,
    0.6175618994,
    0.6454604170,
    0.6736822430,
    0.7022180800,
    0.7310585786,
    0.7601943552,
    0.7896160092,
    0.8193141393,
    0.8492793602,
    0.8795023172,
    0.9099737012,
    0.9406842630,
    0.9716248265,
    1.0027863012,
    1.0341596943,
    1.0657361219,
    1.0975068194,
    1.1294631511,
    1.1615966195,
    1.1938988731,
    1.2263617143,
    1.2589771061,
    1.2917371782,
    1.3246342325,
    1.3576607478,
    1.3908093840,
    1.4240729856,
    1.4574445847,
    1.4909174034,
    1.5244848555,
    1.5581405478,
    1.5918782809,
    1.6256920496,
    1.6595760429,
    1.6935246431,
    1.7275324254,
    1.7615941560,
    1.7957047910,
    1.8298594745,
    1.8640535359,
    1.8982824879,
    1.9325420233,
    1.9668280128,
    2.0011365010,
    2.0354637040,
    2.0698060050,
    2.1041599515,
    2.1385222511,
    2.1728897681,
    2.2072595192,
    2.2416286697,
    2.2759945298,
    2.3103545499,
    2.3447063173,
    2.3790475514,
    2.4133761002,
    2.4476899358,
    2.4819871505,
    2.5162659529,
    2.5505246638,
    2.5847617120,
    2.6189756308,
    2.6531650538,
    2.6873287114,
    2.7214654268,
    2.7555741125,
    2.7896537667,
    2.8237034697,
    2.8577223805,
    2.8917097334,
    2.9256648348,
    2.9595870601,
    2.9934758503,
    3.0273307092,
    3.0611512004,
    3.0949369444,
    3.1286876161,
    3.1624029417,
    3.1960826963,
    3.2297267015,
    3.2633348229,
    3.2969069677,
    3.3304430825,
    3.3639431511,
    3.3974071924,
    3.4308352583,
    3.4642274321,
    3.4975838261,
    3.5309045802,
    3.5641898600,
    3.5974398554,
    3.6306547786,
    3.6638348628,
    3.6969803609,
    3.7300915438,
    3.7631686994,
    3.7962121308,
    3.8292221558,
    3.8621991053,
    3.8951433221,
], dtype=np.float32)

# Pre-computed Mish table (256 entries)
MISH_TABLE = np.array([
    -0.0725917408,
    -0.0742891338,
    -0.0760207890,
    -0.0777871545,
    -0.0795886716,
    -0.0814257740,
    -0.0832988866,
    -0.0852084250,
    -0.0871547939,
    -0.0891383862,
    -0.0911595820,
    -0.0932187471,
    -0.0953162318,
    -0.0974523697,
    -0.0996274761,
    -0.1018418463,
    -0.1040957545,
    -0.1063894518,
    -0.1087231647,
    -0.1110970928,
    -0.1135114078,
    -0.1159662504,
    -0.1184617292,
    -0.1209979180,
    -0.1235748535,
    -0.1261925331,
    -0.1288509127,
    -0.1315499033,
    -0.1342893693,
    -0.1370691249,
    -0.1398889315,
    -0.1427484948,
    -0.1456474613,
    -0.1485854151,
    -0.1515618749,
    -0.1545762896,
    -0.1576280355,
    -0.1607164118,
    -0.1638406370,
    -0.1669998447,
    -0.1701930794,
    -0.1734192917,
    -0.1766773345,
    -0.1799659577,
    -0.1832838034,
    -0.1866294012,
    -0.1900011628,
    -0.1933973770,
    -0.1968162039,
    -0.2002556694,
    -0.2037136597,
    -0.2071879153,
    -0.2106760247,
    -0.2141754190,
    -0.2176833648,
    -0.2211969584,
    -0.2247131192,
    -0.2282285830,
    -0.2317398955,
    -0.2352434054,
    -0.2387352578,
    -0.2422113873,
    -0.2456675111,
    -0.2490991223,
    -0.2525014827,
    -0.2558696166,
    -0.2591983037,
    -0.2624820724,
    -0.2657151937,
    -0.2688916745,
    -0.2720052518,
    -0.2750493868,
    -0.2780172592,
    -0.2809017619,
    -0.2836954965,
    -0.2863907688,
    -0.2889795847,
    -0.2914536470,
    -0.2938043527,
    -0.2960227911,
    -0.2980997422,
    -0.3000256765,
    -0.3017907556,
    -0.3033848332,
    -0.3047974579,
    -0.3060178771,
    -0.3070350411,
    -0.3078376101,
    -0.3084139611,
    -0.3087521975,
    -0.3088401592,
    -0.3086654349,
    -0.3082153764,
    -0.3074771137,
    -0.3064375730,
    -0.3050834961,
    -0.3034014614,
    -0.3013779076,
    -0.2989991594,
    -0.2962514544,
    -0.2931209730,
    -0.2895938700,
    -0.2856563081,
    -0.2812944938,
    -0.2764947145,
    -0.2712433785,
    -0.2655270558,
    -0.2593325207,
    -0.2526467968,
    -0.2454572020,
    -0.2377513952,
    -0.2295174245,
    -0.2207437747,
    -0.2114194165,
    -0.2015338554,
    -0.1910771796,
    -0.1800401088,
    -0.1684140410,
    -0.1561910984,
    -0.1433641719,
    -0.1299269637,
    -0.1158740269,
    -0.1012008033,
    -0.0859036573,
    -0.0699799072,
    -0.0534278515,
    -0.0362467928,
    -0.0184370554,
    0.0000000000,
    0.0190619680,
    0.0387453940,
    0.0590457760,
    0.0799575708,
    0.1014742067,
    0.1235881000,
    0.1462906786,
    0.1695724097,
    0.1934228325,
    0.2178305969,
    0.2427835052,
    0.2682685597,
    0.2942720129,
    0.3207794223,
    0.3477757076,
    0.3752452113,
    0.4031717608,
    0.4315387328,
    0.4603291188,
    0.4895255911,
    0.5191105696,
    0.5490662876,
    0.5793748575,
    0.6100183352,
    0.6409787826,
    0.6722383283,
    0.7037792263,
    0.7355839110,
    0.7676350504,
    0.7999155951,
    0.8324088243,
    0.8650983883,
    0.8979683464,
    0.9310032025,
    0.9641879350,
    0.9975080244,
    1.0309494757,
    1.0644988383,
    1.0981432210,
    1.1318703042,
    1.1656683484,
    1.1995261992,
    1.2334332893,
    1.2673796383,
    1.3013558482,
    1.3353530982,
    1.3693631357,
    1.4033782664,
    1.4373913415,
    1.4713957444,
    1.5053853749,
    1.5393546326,
    1.5732983998,
    1.6072120226,
    1.6410912920,
    1.6749324241,
    1.7087320407,
    1.7424871484,
    1.7761951191,
    1.8098536695,
    1.8434608409,
    1.8770149803,
    1.9105147201,
    1.9439589595,
    1.9773468465,
    2.0106777590,
    2.0439512886,
    2.0771672228,
    2.1103255300,
    2.1434263431,
    2.1764699457,
    2.2094567577,
    2.2423873218,
    2.2752622916,
    2.3080824192,
    2.3408485442,
    2.3735615832,
    2.4062225202,
    2.4388323968,
    2.4713923046,
    2.5039033762,
    2.5363667789,
    2.5687837070,
    2.6011553761,
    2.6334830171,
    2.6657678711,
    2.6980111844,
    2.7302142043,
    2.7623781752,
    2.7945043348,
    2.8265939110,
    2.8586481193,
    2.8906681598,
    2.9226552155,
    2.9546104497,
    2.9865350050,
    3.0184300011,
    3.0502965342,
    3.0821356757,
    3.1139484712,
    3.1457359399,
    3.1774990744,
    3.2092388396,
    3.2409561734,
    3.2726519855,
    3.3043271583,
    3.3359825463,
    3.3676189766,
    3.3992372491,
    3.4308381366,
    3.4624223853,
    3.4939907151,
    3.5255438202,
    3.5570823695,
    3.5886070069,
    3.6201183523,
    3.6516170018,
    3.6831035284,
    3.7145784826,
    3.7460423930,
    3.7774957670,
    3.8089390913,
    3.8403728327,
    3.8717974384,
    3.9032133369,
    3.9346209388,
    3.9660206368,
], dtype=np.float32)

def relu(x: np.ndarray) -> np.ndarray:
    """Apply relu activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.maximum(0, x)

def d_relu(x: np.ndarray) -> np.ndarray:
    """Derivative of relu activation."""
    return np.where(x > 0, 1.0, 0.0)

def leaky_relu(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    """Apply leaky_relu activation.

    Args:
        x: Input array.
        alpha: Parameter for leaky_relu.
    Returns:
        Activated array.
    """
    return np.where(x > 0, x, x * alpha)

def d_leaky_relu(x: np.ndarray, alpha: float = 0.01) -> np.ndarray:
    """Derivative of leaky_relu activation."""
    return np.where(x > 0, 1.0, alpha)

def elu(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Apply elu activation.

    Args:
        x: Input array.
        alpha: Parameter for elu.
    Returns:
        Activated array.
    """
    return np.where(x > 0, x, alpha * (np.exp(np.clip(x, -50, 50)) - 1))

def d_elu(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Derivative of elu activation."""
    return np.where(x > 0, 1.0, alpha * np.exp(np.clip(x, -50, 50)))

def selu(x: np.ndarray, alpha_selu: float = 1.6732632423543772, scale: float = 1.0507009873554805) -> np.ndarray:
    """Apply selu activation.

    Args:
        x: Input array.
        alpha_selu: Parameter for selu.
        scale: Parameter for selu.
    Returns:
        Activated array.
    """
    return scale * np.where(x > 0, x, alpha_selu * (np.exp(np.clip(x, -50, 50)) - 1))

def d_selu(x: np.ndarray, alpha_selu: float = 1.6732632423543772, scale: float = 1.0507009873554805) -> np.ndarray:
    """Derivative of selu activation."""
    return np.ones_like(x)  # derivative not implemented for selu

def gelu(x: np.ndarray) -> np.ndarray:
    """Apply gelu activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0/np.pi) * (x + 0.044715 * x**3)))

def d_gelu(x: np.ndarray) -> np.ndarray:
    """Derivative of gelu activation."""
    return 0.5 * (1.0 + np.tanh(np.sqrt(2.0/np.pi) * (x + 0.044715*x**3))) + 0.5 * x * (1.0 - np.tanh(np.sqrt(2.0/np.pi) * (x + 0.044715*x**3))**2) * np.sqrt(2.0/np.pi) * (1.0 + 0.134145*x**2)

def silu(x: np.ndarray) -> np.ndarray:
    """Apply silu activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x / (1.0 + np.exp(-np.clip(x, -50, 50)))

def d_silu(x: np.ndarray) -> np.ndarray:
    """Derivative of silu activation."""
    return (1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))) + x * np.exp(-np.clip(x, -50, 50)) / (1.0 + np.exp(-np.clip(x, -50, 50)))**2

def mish(x: np.ndarray) -> np.ndarray:
    """Apply mish activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x * np.tanh(np.log(1.0 + np.exp(np.clip(x, -50, 50))))

def d_mish(x: np.ndarray) -> np.ndarray:
    """Derivative of mish activation."""
    return np.tanh(np.log(1.0+np.exp(np.clip(x,-50,50)))) + x * (1.0 - np.tanh(np.log(1.0+np.exp(np.clip(x,-50,50))))**2) * (1.0/(1.0+np.exp(-np.clip(x,-50,50))))

def hard_sigmoid(x: np.ndarray) -> np.ndarray:
    """Apply hard_sigmoid activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.clip(0.2 * x + 0.5, 0, 1)

def d_hard_sigmoid(x: np.ndarray) -> np.ndarray:
    """Derivative of hard_sigmoid activation."""
    return np.ones_like(x)  # derivative not implemented for hard_sigmoid

def hard_swish(x: np.ndarray) -> np.ndarray:
    """Apply hard_swish activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x * np.clip(x / 6.0 + 0.5, 0, 1)

def d_hard_swish(x: np.ndarray) -> np.ndarray:
    """Derivative of hard_swish activation."""
    return np.ones_like(x)  # derivative not implemented for hard_swish

def softsign(x: np.ndarray) -> np.ndarray:
    """Apply softsign activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x / (1.0 + np.abs(x))

def d_softsign(x: np.ndarray) -> np.ndarray:
    """Derivative of softsign activation."""
    return 1.0 / (1.0 + np.abs(x))**2

def softplus(x: np.ndarray) -> np.ndarray:
    """Apply softplus activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.log(1.0 + np.exp(np.clip(x, -50, 50)))

def d_softplus(x: np.ndarray) -> np.ndarray:
    """Derivative of softplus activation."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))

def tanh_shrink(x: np.ndarray) -> np.ndarray:
    """Apply tanh_shrink activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x - np.tanh(x)

def d_tanh_shrink(x: np.ndarray) -> np.ndarray:
    """Derivative of tanh_shrink activation."""
    return np.ones_like(x)  # derivative not implemented for tanh_shrink

def soft_shrink(x: np.ndarray, lam: float = 0.5) -> np.ndarray:
    """Apply soft_shrink activation.

    Args:
        x: Input array.
        lam: Parameter for soft_shrink.
    Returns:
        Activated array.
    """
    return np.where(x > lam, x - lam, np.where(x < -lam, x + lam, 0.0))

def d_soft_shrink(x: np.ndarray, lam: float = 0.5) -> np.ndarray:
    """Derivative of soft_shrink activation."""
    return np.ones_like(x)  # derivative not implemented for soft_shrink

def hard_shrink(x: np.ndarray, lam: float = 0.5) -> np.ndarray:
    """Apply hard_shrink activation.

    Args:
        x: Input array.
        lam: Parameter for hard_shrink.
    Returns:
        Activated array.
    """
    return np.where(np.abs(x) > lam, x, 0.0)

def d_hard_shrink(x: np.ndarray, lam: float = 0.5) -> np.ndarray:
    """Derivative of hard_shrink activation."""
    return np.ones_like(x)  # derivative not implemented for hard_shrink

def bent_identity(x: np.ndarray) -> np.ndarray:
    """Apply bent_identity activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return (np.sqrt(x**2 + 1) - 1) / 2 + x

def d_bent_identity(x: np.ndarray) -> np.ndarray:
    """Derivative of bent_identity activation."""
    return np.ones_like(x)  # derivative not implemented for bent_identity

def gaussian(x: np.ndarray) -> np.ndarray:
    """Apply gaussian activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.exp(-x**2)

def d_gaussian(x: np.ndarray) -> np.ndarray:
    """Derivative of gaussian activation."""
    return np.ones_like(x)  # derivative not implemented for gaussian

def sinc(x: np.ndarray) -> np.ndarray:
    """Apply sinc activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.where(x == 0, 1.0, np.sin(np.pi * x) / (np.pi * x))

def d_sinc(x: np.ndarray) -> np.ndarray:
    """Derivative of sinc activation."""
    return np.ones_like(x)  # derivative not implemented for sinc

def log_log(x: np.ndarray) -> np.ndarray:
    """Apply log_log activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return 1.0 - np.exp(-np.exp(np.clip(x, -50, 50)))

def d_log_log(x: np.ndarray) -> np.ndarray:
    """Derivative of log_log activation."""
    return np.ones_like(x)  # derivative not implemented for log_log

def soft_exponential(x: np.ndarray, alpha: float = 0.0) -> np.ndarray:
    """Apply soft_exponential activation.

    Args:
        x: Input array.
        alpha: Parameter for soft_exponential.
    Returns:
        Activated array.
    """
    return np.where(alpha < 0, -np.log(1 - alpha*(x+alpha)) / alpha, np.where(alpha > 0, (np.exp(alpha*x) - 1)/alpha + alpha, x))

def d_soft_exponential(x: np.ndarray, alpha: float = 0.0) -> np.ndarray:
    """Derivative of soft_exponential activation."""
    return np.ones_like(x)  # derivative not implemented for soft_exponential

def squareplus(x: np.ndarray, b: float = 4.0) -> np.ndarray:
    """Apply squareplus activation.

    Args:
        x: Input array.
        b: Parameter for squareplus.
    Returns:
        Activated array.
    """
    return 0.5 * (x + np.sqrt(x**2 + b))

def d_squareplus(x: np.ndarray, b: float = 4.0) -> np.ndarray:
    """Derivative of squareplus activation."""
    return np.ones_like(x)  # derivative not implemented for squareplus

def pflug(x: np.ndarray) -> np.ndarray:
    """Apply pflug activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.clip(x, -1, 1) + (x - np.clip(x, -1, 1)) / (1 + np.abs(x - np.clip(x, -1, 1)))

def d_pflug(x: np.ndarray) -> np.ndarray:
    """Derivative of pflug activation."""
    return np.ones_like(x)  # derivative not implemented for pflug

def serf(x: np.ndarray) -> np.ndarray:
    """Apply serf activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return x / np.sqrt(1 + np.exp(-2 * np.clip(x, -50, 50)))

def d_serf(x: np.ndarray) -> np.ndarray:
    """Derivative of serf activation."""
    return np.ones_like(x)  # derivative not implemented for serf

def snake(x: np.ndarray, a: float = 1.0) -> np.ndarray:
    """Apply snake activation.

    Args:
        x: Input array.
        a: Parameter for snake.
    Returns:
        Activated array.
    """
    return x + (1/a) * np.sin(a * x)**2

def d_snake(x: np.ndarray, a: float = 1.0) -> np.ndarray:
    """Derivative of snake activation."""
    return np.ones_like(x)  # derivative not implemented for snake

def cone(x: np.ndarray) -> np.ndarray:
    """Apply cone activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.sqrt(1 + x**2) - 1

def d_cone(x: np.ndarray) -> np.ndarray:
    """Derivative of cone activation."""
    return np.ones_like(x)  # derivative not implemented for cone

def wave(x: np.ndarray) -> np.ndarray:
    """Apply wave activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.where(x != 0, (x / np.abs(x)) * (1 - np.exp(-np.abs(x))), 0.0)

def d_wave(x: np.ndarray) -> np.ndarray:
    """Derivative of wave activation."""
    return np.ones_like(x)  # derivative not implemented for wave

def arctan(x: np.ndarray) -> np.ndarray:
    """Apply arctan activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.arctan(x)

def d_arctan(x: np.ndarray) -> np.ndarray:
    """Derivative of arctan activation."""
    return np.ones_like(x)  # derivative not implemented for arctan

def quartic(x: np.ndarray) -> np.ndarray:
    """Apply quartic activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.where(x >= 0, x**4, np.zeros_like(x))

def d_quartic(x: np.ndarray) -> np.ndarray:
    """Derivative of quartic activation."""
    return np.ones_like(x)  # derivative not implemented for quartic

def sine(x: np.ndarray) -> np.ndarray:
    """Apply sine activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return np.where(x != 0, np.sin(x) / x, 1.0)

def d_sine(x: np.ndarray) -> np.ndarray:
    """Derivative of sine activation."""
    return np.ones_like(x)  # derivative not implemented for sine

def erf_act(x: np.ndarray) -> np.ndarray:
    """Apply erf_act activation.

    Args:
        x: Input array.
    Returns:
        Activated array.
    """
    return 0.5 * (1 + np.vectorize(math.erf)(x / np.sqrt(2)))

def d_erf_act(x: np.ndarray) -> np.ndarray:
    """Derivative of erf_act activation."""
    return np.ones_like(x)  # derivative not implemented for erf_act


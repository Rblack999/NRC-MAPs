import easy_biologic as ebl
import easy_biologic.base_programs as blp

# create device
bl = ebl.BiologicDevice('USB0')

# create mpp program
params = {
	'run_time': 10* 60
}

mpp = blp.MPP(
    bl,
    params,
    channels = [0]
)

# run program
mpp.run( 'data' )

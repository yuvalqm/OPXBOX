import numpy as np
import matplotlib.pyplot as plt
import pytest

def resample_trace(x, y, points):
	assert len(x) == len(y)
	t = np.linspace(0, len(x), points)
	x = np.interp(t, np.arange(len(x)), x)
	y = np.interp(t, np.arange(len(y)), y)
	return np.array([x, y])

def calc_distances(x, y):
	x = np.asarray(x)
	y = np.asarray(y)
	return np.sqrt(np.square(y[:-1]-y[1:])+np.square(x[:-1]-x[1:]))

@pytest.mark.parametrize("x, y, exp", [
	([0, 0], [0, 0], 0), 
	([0, 0], [1, 1], 0), 
	([0, 1], [0, 0], 1), 
	([0, 0], [1, 0], 1), 
	([0, 0], [0, 1], 1), 
	([0, 1], [0, 1], np.sqrt(2)), 
	([1, 0], [1, 0], np.sqrt(2)), 
])
def test_distances(x, y, exp):
	res = calc_distances(x, y)
	assert res.shape == (1, )
	assert res[0] == pytest.approx(exp)

def sample_with_speed(x, y, speed):
	# speed is to be given in sample/volt
	assert len(x) == len(y)
	
	distances = calc_distances(x, y)
	cumdis = np.cumsum(distances)
	raise NotImplementedError()
	return resample_trace(x, y, cumdis*speed)

def get_ship_pulse(points):
	x = [-.5, -1, 1, -1, -.5]
	y = [0, -.5, 0, .5, 0]
	return resample_trace(x, y, points)

def get_ray_pulse(points):
	x = [-.5, .5]
	y = [0, 0]
	return resample_trace(x, y, points)

def get_asteroid_pulse(points, seed=5, arms=10):

	t = np.linspace(0, 1, arms+1)[:-1]*2*np.pi

	rng = np.random.default_rng(seed=seed)
	r = rng.uniform(-.4, .4, arms)
	phi = rng.uniform(-.02, .02, arms)*2*np.pi

	x = np.cos(t+phi)*(1+r)
	y = np.sin(t+phi)*(1+r)
	x = np.concatenate([x, [x[0]]])
	y = np.concatenate([y, [y[0]]])

	return resample_trace(x, y, points)

def get_border_pulse(points):
	x = [0, 1, 1, 0, 0]
	y = [0, 0, 1, 1, 0]
	return resample_trace(x, y, points)*2-1

def draw_example(pulse):
	plt.plot(*pulse)
	plt.show()

if __name__ == '__main__':
	draw_example(get_ship_pulse(100))
	draw_example(get_ray_pulse(100))
	draw_example(get_asteroid_pulse(100))
	draw_example(get_border_pulse(100))
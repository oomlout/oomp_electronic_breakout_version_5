$fn = 50;

difference() {
	union() {
		translate(v = [7.414999999999999, 0.0, 0]) {
			hull() {
				translate(v = [-32.085, 32.29, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [32.085, 32.29, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-32.085, -32.29, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [32.085, -32.29, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
	}
	union() {
		translate(v = [37.5, -30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [37.5, -15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [37.5, 0.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [37.5, 15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [37.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [37.5, -22.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [37.5, -7.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [37.5, 7.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [37.5, 22.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

$fn = 50;

difference() {
	union() {
		translate(v = [6.1675, 0.0, 0]) {
			hull() {
				translate(v = [-18.3325, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [18.3325, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-18.3325, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [18.3325, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
	}
	union() {
		translate(v = [22.5, -22.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, -7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 22.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, -15.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [22.5, 0.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [22.5, 15.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

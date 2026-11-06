$fn = 50;

difference() {
	union() {
		translate(v = [6.9, 7.5, 0]) {
			hull() {
				translate(v = [-17.6, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [17.6, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-17.6, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [17.6, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
	}
	union() {
		translate(v = [22.5, -15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 0.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, -7.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [22.5, 7.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [22.5, 22.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [7.5, 15.0, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [22.5, 7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, 7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [22.5, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
	}
}

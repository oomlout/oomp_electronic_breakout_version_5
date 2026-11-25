$fn = 50;

difference() {
	union() {
		hull() {
			translate(v = [-10.7, 39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [10.7, 39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-10.7, -39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [10.7, -39.5, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
	}
	union() {
		translate(v = [-7.5, -37.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [-7.5, 37.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [7.5, -37.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [7.5, 37.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [0.0, -37.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [0.0, 37.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

$fn = 50;

difference() {
	union() {
		hull() {
			translate(v = [-32.0, 10.7, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [32.0, 10.7, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-32.0, -10.7, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [32.0, -10.7, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
	}
	union() {
		translate(v = [-30.0, -7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [-30.0, 7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [30.0, -7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [30.0, 7.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [-30.0, 0.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [30.0, 0.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

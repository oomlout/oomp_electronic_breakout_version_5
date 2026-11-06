$fn = 50;

difference() {
	union() {
		hull() {
			translate(v = [-17.0, 24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [17.0, 24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-17.0, -24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [17.0, -24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
	}
	union() {
		translate(v = [-15.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [0.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [0.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [15.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-15.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, -15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, 0.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, 15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-7.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-7.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [0.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [0.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [7.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [7.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, -15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, -7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, 0.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, 7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, 15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [0, 7.5, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [15, 0.0, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-15, 0.0, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [15, 15.0, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-15, 15.0, -1]) {
			cylinder(h = 8, r = 1.8);
		}
	}
}

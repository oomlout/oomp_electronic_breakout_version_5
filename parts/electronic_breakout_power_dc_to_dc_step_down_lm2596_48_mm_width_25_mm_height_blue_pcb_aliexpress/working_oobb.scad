$fn = 50;

difference() {
	union() {
		hull() {
			translate(v = [-39.5, 24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [39.5, 24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-39.5, -24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [39.5, -24.5, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
		translate(v = [18.0, -10.0, 3.0]) {
			cylinder(h = 6, r = 3.75);
		}
		translate(v = [-18.0, 10.0, 3.0]) {
			cylinder(h = 6, r = 3.75);
		}
	}
	union() {
		translate(v = [18.0, -10.0, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.8);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-18.0, 10.0, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.8);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-37.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-22.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-22.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-7.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-7.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [7.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [7.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [22.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [22.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, -7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 7.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, -15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, -7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 0.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-30.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-30.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-22.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-22.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, -22.5, -100.0]) {
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
		translate(v = [15.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [22.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [22.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [30.0, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [30.0, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 0.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 7.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 15.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 22.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-27.5, 2.5, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [-30.0, -7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-30.0, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-15.0, -7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-15.0, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [17.5, 2.5, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [15.0, -7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [15.0, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [30.0, -7.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [30.0, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
	}
}

$fn = 50;

difference() {
	union() {
		translate(v = [7.5, 0.0, 0]) {
			hull() {
				translate(v = [-17.0, 17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [17.0, 17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-17.0, -17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [17.0, -17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
		translate(v = [7.5, 5.5, 3.0]) {
			cylinder(h = 6, r = 2.75);
		}
		translate(v = [7.5, -5.5, 3.0]) {
			cylinder(h = 6, r = 2.75);
		}
	}
	union() {
		translate(v = [7.5, 5.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.35);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.0);
						}
					}
					union();
				}
			}
		}
		translate(v = [7.5, -5.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.35);
						}
						translate(v = [0, 0, -9.0]) {
							cylinder(h = 9, r = 1.0);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, 15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [7.5, 15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 15.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [0.0, 15.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [15.0, 15.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [7.5, 0, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [0.0, -15, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [0.0, 15, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [15.0, -15, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [15.0, 15, -1]) {
			cylinder(h = 8, r = 1.8);
		}
	}
}

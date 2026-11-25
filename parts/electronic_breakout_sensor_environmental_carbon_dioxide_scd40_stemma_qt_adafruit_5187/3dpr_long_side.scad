$fn = 50;

difference() {
	union() {
		translate(v = [0.0, 7.5, 0]) {
			hull() {
				translate(v = [-10.7, 17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [10.7, 17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-10.7, -17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [10.7, -17.0, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
		translate(v = [-10.16, 8.89, 3.0]) {
			cylinder(h = 3, r = 3.25);
		}
		translate(v = [10.16, 8.89, 3.0]) {
			cylinder(h = 3, r = 3.25);
		}
		translate(v = [-10.16, -8.89, 3.0]) {
			cylinder(h = 3, r = 3.25);
		}
		translate(v = [10.16, -8.89, 3.0]) {
			cylinder(h = 3, r = 3.25);
		}
	}
	union() {
		translate(v = [-10.16, 8.89, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
						translate(v = [0, 0, -1.0]) {
							cylinder(h = 1.0, r1 = 1.55, r2 = 3.45);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.55);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
					}
					union();
				}
			}
		}
		translate(v = [10.16, 8.89, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
						translate(v = [0, 0, -1.0]) {
							cylinder(h = 1.0, r1 = 1.55, r2 = 3.45);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.55);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
					}
					union();
				}
			}
		}
		translate(v = [-10.16, -8.89, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
						translate(v = [0, 0, -1.0]) {
							cylinder(h = 1.0, r1 = 1.55, r2 = 3.45);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.55);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
					}
					union();
				}
			}
		}
		translate(v = [10.16, -8.89, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
						translate(v = [0, 0, -1.0]) {
							cylinder(h = 1.0, r1 = 1.55, r2 = 3.45);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.55);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.25);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, 22.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [7.5, 22.5, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [0.0, 22.5, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

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
		translate(v = [-10.16, 6.35, 3.0]) {
			cylinder(h = 3, r = 2.75);
		}
		translate(v = [10.16, 6.35, 3.0]) {
			cylinder(h = 3, r = 2.75);
		}
		translate(v = [-10.16, -6.35, 3.0]) {
			cylinder(h = 3, r = 2.75);
		}
		translate(v = [10.16, -6.35, 3.0]) {
			cylinder(h = 3, r = 2.75);
		}
	}
	union() {
		translate(v = [-10.16, 6.35, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.35);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
					}
					union();
				}
			}
		}
		translate(v = [10.16, 6.35, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.35);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
					}
					union();
				}
			}
		}
		translate(v = [-10.16, -6.35, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.35);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
					}
					union();
				}
			}
		}
		translate(v = [10.16, -6.35, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
						}
						translate(v = [0, 0, -0.85]) {
							cylinder(h = 0.85, r1 = 1.35, r2 = 3.0);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.35);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.0);
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

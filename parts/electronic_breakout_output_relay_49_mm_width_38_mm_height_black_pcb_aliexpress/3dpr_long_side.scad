$fn = 50;

difference() {
	union() {
		translate(v = [0.0, 7.5, 0]) {
			hull() {
				translate(v = [-24.5, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [24.5, 24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [-24.5, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
				translate(v = [24.5, -24.5, 0]) {
					cylinder(h = 3, r = 5);
				}
			}
		}
		translate(v = [22.0, 16.5, 3.0]) {
			cylinder(h = 3, r = 3.75);
		}
		translate(v = [22.0, -16.5, 3.0]) {
			cylinder(h = 3, r = 3.75);
		}
		translate(v = [-22.0, 16.5, 3.0]) {
			cylinder(h = 3, r = 3.75);
		}
		translate(v = [-22.0, -16.5, 3.0]) {
			cylinder(h = 3, r = 3.75);
		}
	}
	union() {
		translate(v = [22.0, 16.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [22.0, -16.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-22.0, 16.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-22.0, -16.5, 0]) {
			rotate(a = [0, 180, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-22.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [-7.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [7.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [22.5, 30.0, -1]) {
			cylinder(h = 5, r = 3.25);
		}
		translate(v = [-15.0, 30.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [0.0, 30.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
		translate(v = [15.0, 30.0, -1]) {
			cylinder(h = 5, r = 1.8);
		}
	}
}

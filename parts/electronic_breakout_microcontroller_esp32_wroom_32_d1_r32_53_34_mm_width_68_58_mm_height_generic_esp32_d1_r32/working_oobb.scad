$fn = 50;

difference() {
	union() {
		hull() {
			translate(v = [-39.5, 47.0, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [39.5, 47.0, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [-39.5, -47.0, 0]) {
				cylinder(h = 3, r = 5);
			}
			translate(v = [39.5, -47.0, 0]) {
				cylinder(h = 3, r = 5);
			}
		}
		translate(v = [22.5, -37.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [-7.5, -37.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [22.5, -22.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [-7.5, -22.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [22.5, 22.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [-7.5, 22.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [22.5, 37.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
		translate(v = [-7.5, 37.5, 3.0]) {
			cylinder(h = 3, r = 4.962);
		}
	}
	union() {
		translate(v = [22.5, -37.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, -37.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [22.5, -22.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, -22.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [22.5, 22.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, 22.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [22.5, 37.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, 37.5, 3]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 104) {
							polygon(points = [[3.4619999999999997, 0.0], [1.7310000000000003, 2.9981799479017264], [-1.7309999999999992, 2.9981799479017264], [-3.4619999999999997, 4.2397272186481365e-16], [-1.7310000000000014, -2.998179947901726], [1.7309999999999977, -2.9981799479017277]]);
						}
					}
					union();
				}
			}
		}
		translate(v = [-37.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, -30.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, -15.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 0.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 15.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 30.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-22.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-22.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-7.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-7.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [7.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [7.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [22.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [22.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, -30.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, -15.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 0.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 15.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 30.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [37.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 3.25);
		}
		translate(v = [-37.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, -37.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, -30.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
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
		translate(v = [-37.5, 30.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 37.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-37.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-30.0, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-30.0, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-22.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-22.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-15.0, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-7.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [-7.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [0.0, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [0.0, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [7.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [7.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [15.0, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [22.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [22.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [30.0, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [30.0, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -37.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, -30.0, -100.0]) {
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
		translate(v = [37.5, 30.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 37.5, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [37.5, 45.0, -100.0]) {
			cylinder(h = 200, r = 1.8);
		}
		translate(v = [7.5, -30.0, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [22.5, -37.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, -37.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [22.5, -22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, -22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [7.5, 30.0, -1]) {
			cylinder(h = 4, r = 6);
		}
		translate(v = [22.5, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, 22.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [22.5, 37.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
		translate(v = [-7.5, 37.5, -1]) {
			cylinder(h = 8, r = 1.8);
		}
	}
}

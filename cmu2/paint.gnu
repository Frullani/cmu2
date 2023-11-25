set xrange [0:1]
set yrange [0:4]
set title "x1 Plot"
plot 'x1_0.txt' with points pt 7 linecolor "red" title 'alpha=0', 'x1_1.txt' with points pt 7 linecolor "blue" title 'alpha=0.1', 'x1_2.txt' with points pt 7 linecolor "black" title 'alpha=1', 'x1_3.txt' with points pt 7 linecolor "yellow" title 'alpha=3'


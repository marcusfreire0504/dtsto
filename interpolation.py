#
# dtsto: day trade and swing trade operate
# ==========================================
#
# Este código faz parte de um algoritmo construído com o objetivo de atuar no mercado financeiro
# de forma independente
#
# @author      Isak Ruas <isakruas@gmail.com>
#
# @license     Este código é disponibilizado sobre a Licença Pública Geral (GNU) V3.0
#              Mais detalhes em: https://github.com/isakruas/dtsto/blob/master/LICENSE
#
# @link        Homepage:     http://nrolabs.com/dtsto/
#              GitHub Repo:  https://github.com/isakruas/dtsto/
#              README:       https://github.com/isakruas/dtsto/blob/master/README.md
#
# @version     1.0.00
#

import numpy


# Esta função retorna os coeficientes de uma função polinomial que passa por um conjunto de pontos dados. Há duas
# formas de se utilizar esta função. A primeira, passa-se somente as imagens geradas por uma função polinomial g(x);
# neste caso, a função retornará os coeficientes, considerando que o domínio da função g(x) vai de 1 até n,
# no qual n é a quantidade de imagens geradas passadas. A segunda, especifica-se o domínio e a imagem da função g(x).
# Em ambos os casos, a função retorna-se os coeficiente a0, a1, a2, …, an da função g(x) =
# a0*x**0++a1*x**1+...+an*x**n.

def interpolation(**args):
    if 'domain' in args and 'image' in args:
        domain = args['domain']
        image = args['image']
        if len(domain) == len(image):
            matrix = numpy.zeros((len(image), len(image)), dtype=float)
            for line in range(0, len(domain)):
                for column in range(0, len(domain)):
                    matrix[line][column] = domain[line] ** column

            matrix_inv = numpy.linalg.inv(matrix)
            coefficients = matrix_inv.dot(image)
            return coefficients
        else:
            pass
    elif 'image' in args:
        image = args['image']
        matrix = numpy.zeros((len(image), len(image)), dtype=float)
        for line in range(0, len(matrix)):
            for column in range(0, len(matrix)):
                matrix[line][column] = (line + 1) ** column
        matrix_inv = numpy.linalg.inv(matrix)
        coefficients = matrix_inv.dot(image)
        return coefficients
    else:
        pass

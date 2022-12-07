# ENZ  : Liste des enzymes utilisables (indexé par un numéro du tableau MOL)
# REAC : Liste des entrées (indexé par un numéro du tableau MOL)
# prod : produit à obtenir (indexé par un numéro du tableau MOL)
# etqt : étiquette à avoir ?
# n    : nb max d'étaps ?

def pluscourtchemin(ENZ,REAC,prod,n,imprime,reaction,MOL,REACTIONS,REACPARMOL):

    """ PRESENCE : liste des molécules présente.
    Evolue au cours de l'algorithme.
    Chaque case coorespond à une molécule et est de la forme :
    [boolean marquant la présence,
    liste des réaction l'ayant produit selon le triplet (numéro de réaction, numéro d'étape, étiquette),
    liste des étiquettes avec lesquelles la molécule a été produite,
    liste des doublets (numéro d'étape, étiquette) avec lesquelles la molécule a été produite]"""

    """     Initialisation des variables """

    # Initialisation de chaque molécule comme absente
    PRESENCE = []
    for k in range(0, len(MOL)):
        PRESENCE.append([False, [], [], []])
    nbetape = 0  # Nombre d'étapes réactionnels pour obtenir le produis cherché (la plus longue chaine d'étapes)
    nbmol = 0  # Nombre total de molécules présente (au sens qui ont été produite à un moment)
    nbmolbis = 0

    ##initialisation de la liste de présence pour les réactifs de REAC (formés à l'étape -1, par la réaction 0 qui n'existe pas)
    for k in range(len(REAC)):
        if k == 0:
            PRESENCE[REAC[k]] = [True, [(-1, 0, 'a')], ['a'], [(-1, 'a')]]
        if k == 1:
            PRESENCE[REAC[k]] = [True, [(-1, 0, 'b')], ['b'], [(-1, 'b')]]
        nbmol += 1

    for a in ENZ:  ##initialisation de la liste de présence pour ajouter les enzymes
        PRESENCE[a] = [True, [(-1, 0, 'e')], ['e'], [(-1, 'e')]]
        nbmol += 1

        """ Boucle de recherche descendante """
    ##exploration des différents chemins réactionnels par itérations successives
    while (nbetape < n):
        nbetape += 1
        nbmolbis = nbmol
        ## on veut que les molécules produites soient notées présentes uniquement à la fin de l'étape pour ne pas mélanger les étapes. On ne met donc pas à jour directement PRESENCE, mais d'abord PRESENCEBIS.
        PRESENCEBIS = []

        ## itération sur les molécules présences
        for num_molecule in range(len(PRESENCE)):
            if PRESENCE[num_molecule][0]:
                # On récupére la liste des réactions où la molécule intervient
                REACPOT = REACPARMOL[num_molecule]

                ## itération sur les réactions impliquant la molécule en tant que réactif
                for a in REACPOT:

                    reactifs_presents = True
                    for b in REACTIONS[a][0]:
                        ## on teste si tout les réactifs de la réaction en question sont présents
                        if PRESENCE[b][0] == False:
                            reactifs_presents = False
                            break

                    if reactifs_presents:  ##si oui on met à jour la liste de présence
                        ## cas où il y a un seul réactif (marginal) / REACTIONS[a][0] est la liste des réactifs)
                        if len(REACTIONS[a][0]) == 1:
                            mol = REACTIONS[a][0][0]  ## unique réactif
                            ##étape de mise à jour de la liste de présence (molécule produite à telle étape, avec telle étiquette, par telle réaction)
                            for e in PRESENCE[mol][2]:
                                for produit in REACTIONS[a][1]:
                                    if e not in PRESENCE[produit][2]:
                                        PRESENCEBIS.append((produit, e))
                                    if (a, e) not in PRESENCE[produit][3]:
                                        PRESENCE[produit][1].append((a, nbetape, e))  ## ici on se permet de mettre à jour PRESENCE et pas PRESENCEBIS car cela n'a pas d'influence.
                                        PRESENCE[produit][3].append((a, e))
                                    if PRESENCE[produit][0] == False:
                                        nbmol += 1

                        if len(REACTIONS[a][0]) == 2:  ## cas où il y a deux réactifs (cas commun)
                            mol1 = REACTIONS[a][0][0]
                            mol2 = REACTIONS[a][0][1]
                            for e1 in PRESENCE[mol1][2]:
                                for e2 in PRESENCE[mol2][2]:
                                    e = bin(e1,e2)  ##utilisation de la relation binaire pour la propagation des étiquettes
                                    for produit in REACTIONS[a][1]:  ##REACTIONS [a][1] correspond aux produits de la réaction a
                                        if e not in PRESENCE[produit][2]:
                                            PRESENCEBIS.append((produit, e))
                                        if (a, e) not in PRESENCE[produit][3]:  ##contingent si on veut juste le plus court chemin
                                            PRESENCE[produit][3].append((a, e))
                                            PRESENCE[produit][1].append((a, nbetape, e))
                                        if PRESENCE[produit][0] == False:
                                            nbmol += 1

        # mise à jour de PRESENCE à partir de PRESENCE BIS
        for a in PRESENCEBIS:
            if a[1] not in PRESENCE[a[0]][2]:
                PRESENCE[a[0]][2].append(a[1])
            PRESENCE[a[0]][0] = True

        """ Fin boucle de recherche  """

        """ Boucle de recherche ascendante """

    #print("Mécanismes réactionnels obtenus pour le produit en " + str(nbetape) + " étapes maximum avec l'étiquette "+etqt+" :")
    #print(PRESENCE[prod][0:2])
    #print("")
    # On vérifie que le produit voulu a été créé
    if (PRESENCE[prod][0] == False):
        print("impossible d'arriver au produit")
        print("nombre d'étapes=" + str(nbetape))
        print("nombre de molecules=" + str(nbmol))
        print('********************************************')
        print('')
        return (False)

    MECANISMES = []  ## liste des mécanismes sous forme de doublet (MECANISME, étiquette)
    MECANISME = []  ## mécanisme sous forme d'une liste d'étapes, chaque étape étant une liste de réactions


    #print(PRESENCE[numero('DDib5')])

    # une fois le produit trouvé, on remonte la chaîne réactionnelle pour écrire le mécanisme par étapes
    for meca in PRESENCE[prod][1]:
        MECANISME=[]
        presence_cycles=False ## booléen pour éviter que des cycles ne se répètent
        nbetape = meca[1]
        PROD = [(prod,meca[2])]
        while nbetape > 0:
            # print(nbetape)
            ETAPE = []
            PRODBIS = []
            #print([MOL[prod[0]] for prod in PROD])

            # pour chaque produit on retrouve les réactifs qui l'ont formé et on leur associe l'étiquette correspondante
            for a in PROD:
                # recherche du numéro r de la réaction ayant permis la production de la molécule a en nbetape étapes
                r = -1
                for reac in PRESENCE[a[0]][1]:
                    if reac[1] == nbetape and reac[2] == a[1] and reac[1] == min([reac[1] for reac in PRESENCE[a[0]][1] if reac[2] == a[1]]):
                        r = reac[0]
                        break
                if r == -1: ## potentiellement contingent
                    #print(nbetape,MOL[a[0]],a[1])
                    PRODBIS.append(a)
                else:
                    ETAPE.append(r)
                    reactifs = REACTIONS[r][0]
                    produits = REACTIONS[r][1]
                    for p in produits:
                        if p == prod and nbetape < meca[1]-1:
                            presence_cycles=True #détection d'un cycle rendant le mécanisme invalide : un mécanisme invalide est un mécanisme dans le quel le produit final n'apparait pas seulement dans la dernière réaction
                            break ##on veut sortir de 3 boucles imbriquées donc on va rappeler ce break
                    if presence_cycles:
                        break
                    if len(reactifs) == 1:
                        PRODBIS.append((reactifs[0], a[1]))
                    else:  ##on suppose la molécularité inférieure ou égale à 2
                        eti = a[1]
                        r20 = reactifs[0]  # réactif 1
                        r21 = reactifs[1]  # réactif 2
                        P0 = PRESENCE[r20][1]  # réactions ayant produit r20
                        P1 = PRESENCE[r21][1]  # réactions ayant produit r21

                        # Création de L0 et L1, liste des étiquettes avec lesquels r20 a pu être formé avant nbetape
                        L0 = [d[2] for d in PRESENCE[r20][1] if d[1] <= nbetape - 1]
                        L1 = [d[2] for d in PRESENCE[r21][1] if d[1] <= nbetape - 1]
                        # print(L0)
                        # print(L1)
                        if eti == 'e':
                            for re in reactifs:
                                PRODBIS.append((re, 'e'))
                        if eti == 'a':
                            if 'a' in L0:
                                PRODBIS.append((r20, 'a'))
                            else:
                                PRODBIS.append((r20, 'e'))
                            if 'a' in L1:
                                PRODBIS.append((r21, 'a'))
                            else:
                                PRODBIS.append((r21, 'e'))
                        if eti == 'b':
                            if 'b' in L0:
                                PRODBIS.append((r20, 'b'))
                            else:
                                PRODBIS.append((r20, 'e'))
                            if 'b' in L1:
                                PRODBIS.append((r21, 'b'))
                            else:
                                PRODBIS.append((r21, 'e'))
                        if eti == 'ab':
                            sel = selec2ab(L0, L1)
                            if sel[0] != 'o':
                                PRODBIS.append((reactifs[0], sel[0]))
                            if sel[1] != 'o':
                                PRODBIS.append((reactifs[1], sel[1]))
                            if sel[0] == 'o' and sel[1] != 'o':
                                r0 = reactifs[0]
                                for r in PRESENCE[r0][1]:
                                    if (r[2] == 'a') or (r[2] == 'b'):
                                        PRODBIS.append((r0, r[2]))
                                        break
                            if sel[1] == 'o' and sel[0] != 'o':
                                r0 = reactifs[1]
                                for r in PRESENCE[r0][1]:
                                    if (r[2] == 'a') or (r[2] == 'b'):
                                        PRODBIS.append((r0, r[2]))
                                        break
                            if sel[0] == 'o' and sel[1] == 'o':
                                r0 = reactifs[0]
                                r1 = reactifs[1]
                                for r in PRESENCE[r0][1]:
                                    if (r[2] == 'a') or (r[2] == 'b'):
                                        PRODBIS.append((r0, r[2]))
                                        etq = r[2]
                                        break
                                for r in PRESENCE[r1][1]:
                                    if ((r[2] == 'a') or (r[2] == 'b')) and r[2] != etq:
                                        PRODBIS.append((r1, r[2]))
                if presence_cycles:
                    break ##break prolongeant un autre pour sortir de 3 boucles successives
            if presence_cycles:
                break ##break prolongeant un autre pour sortir de 3 boucles successives
            if ETAPE != []:
                MECANISME = [ETAPE] + MECANISME
            # print([MOL[a[0]] for a in PROD])
            # print([MOL[a[0]] for a in PRODBIS])
            PROD = []
            for a in PRODBIS:
                PROD.append(a)
            PRODBIS = []
            nbetape=nbetape-1
        Enzs = []
        #print(presence_cycles)
        if presence_cycles==False:
            for mol in PROD:
                if mol != numero(REAC[0],MOL) and mol != numero(REAC[1],MOL):
                    Enzs.append(mol[0])
            MECANISMES.append((MECANISME,meca[2],Enzs))




    print('Les mécanismes après sélection sont les suivants')
    print(MECANISMES)
    print(" ")
    if imprime==True: ##Si on décide de print les mécanismes sous forme de texte, on les affiche
        i=0
        for meca in MECANISMES:
            i+=1
            print("mécanisme "+str(i)+":")
            txt=mecatexte(meca[0],reaction)
            for a in txt:
                print(a)
            print(" ")
    print('********************************************')
    return MECANISMES


def bin(c, d):  ##relation binaire de propagation des étiquettes
    if c == 'a' and d == 'b':
        return('ab')
    if c == 'b' and d == 'a':
        return('ab')
    if c == 'ab' or d == 'ab':
        return('ab')
    if c == 'a' or d == 'a':
        return('a')
    if c == 'b' or d == 'b':
        return('b')
    else:
        return('e')


def selec(L):  ##fonction utile pour selec2ab
    if 'ab' in L:
        return('ab')
    if 'a' in L and 'b' in L:
        return('o')
    if 'b' in L:
        return('b')
    if 'a' in L:
        return('a')
    else:
        return('e')


def selec2ab(L1,L2):  ##cette fonction aide l'algorithme de remontée. Le but est, quand le produit d'une réaction est avec l'étiquette 'ab', de choisir avec quelles étiquettes on va considérer les réactifs qui ont mené à ce produit. Si on a 'o' on peut choisir 'a' ou 'b' indifféremment.
    l1 = selec(L1)
    l2 = selec(L2)
    if l2 == 'o':
        if l1 == 'ab':
            return('ab', 'o')
        if l1 == 'b':
            return('b', 'a')
        if l1 == 'a':
            return('a', 'b')
        if l1 == 'o':
            return('o', 'o')
    if l1 == 'o':
        if l2 == 'o':
            return('o', 'o')
        if l2 == 'b':
            return('a', 'b')
        if l2 == 'a':
            return('b', 'a')
        if l2 == 'ab':
            return('o', 'ab')
    return(l1, l2)


def numero(enzyme,MOL):  ##retourne le numéro correspondant à un nom d'enzyme
    for i in range(0, len(MOL)):
        if MOL[i] == enzyme:
            return (i)


def numero2(L,MOL):  ##retourne les numéros correspondant aux noms d'enzymes d'une liste d'enzymes
    L2 = []
    for k in range(0, len(L)):
        L2.append(numero(L[k],MOL))
    return (L2)


def mecatexte(MECANISME,reaction):  ##simple fonction qui convertit le mécanisme réactionnel renvoyé par l'algorithme en un texte lisible pour l'utilisateur.
    MT = []
    for k in range(len(MECANISME)):
        ET = []
        for a in MECANISME[k]:
            ET.append(reaction[a])
        MT.append(ET)
    return (MT)


# Prend un numéro de molécule en paramétre et renvoie le numéro de molécule faisant la logique "non" ainsi que le numéro de réaction
def molécule_non_v1(numéro_molécule,MOL,REACTIONS):
    if(MOL[numéro_molécule].endswith('ext')): #Il faut prendre la molécule une fois dans la cellule pour chercher un non
        nom_molécule=MOL[numéro_molécule]
        if MOL[numéro_molécule+1]==nom_molécule[:-3]:
            numéro_molécule=numéro_molécule+1
        else:
            for num_molécule_boucle,nom_molécule_boucle in enumerate(MOL):
                if nom_molécule_boucle==nom_molécule[:-3]:
                    numéro_molécule=num_molécule_boucle
                    break
        

    for num_reac, réacion_i in enumerate(REACTIONS): # La molécule une fois rentré ne peut pas sortir, donc pas besoin d'exclure la réaction retour (sauf s'il la réaction A=>Aext devient possible)
        if numéro_molécule in réacion_i[0]:
            if réacion_i[0][0] == numéro_molécule:
                molécule_non = réacion_i[1][0]
            else:
                molécule_non = réacion_i[0][0]
            
            print(f"Molécule non : {MOL[molécule_non]}")
            réaction_négation=REACTIONS[num_reac]
            print(f"Réaction de négation : {' + '.join([MOL[indice_réactif] for indice_réactif in réaction_négation[0]])} => {MOL[réaction_négation[1][0]]}")

            return molécule_non, num_reac
    raise Exception("Aucune molécule 'non' trouvée")


# ET : '+'
# OU : '|'
# NON : '!'
# OU EXCLUSIF : '-'
# symbole réaction : '=>'
def résolution_équation(équation_logique,nb_réactions_max,reaction,MOL,REACTIONS,REACPARMOL):
    liste_mots = équation_logique.split(" ")

    # Récupération du numéro du 1er réactif
    if liste_mots[0][0] == '!':
        réactif_1, num_reac_non1 = molécule_non_v1(numero(liste_mots[0][1:],MOL),MOL,REACTIONS)
    else:
        réactif_1 = numero(liste_mots[0],MOL)

    # Récupération du numéro du 2eme réactif
    if liste_mots[2][0] == '!':
        réactif_2, num_reac_non2 = molécule_non_v1(numero(liste_mots[2][1:],MOL),MOL,REACTIONS)
    else:
        réactif_2 = numero(liste_mots[2],MOL)

    produit = numero(liste_mots[4],MOL)

    if liste_mots[1] == '+':
        #print(f"MECAS=pluscourtchemin({numero2(ENZ)},[{réactif_1}, {réactif_2}],{produit},{nb_réactions_max}, True)")
        MECAS = pluscourtchemin(numero2(ENZ,MOL), [réactif_1, réactif_2], produit, nb_réactions_max, True,reaction,MOL,REACTIONS,REACPARMOL)
        mt = mecatexte(MECAS[0][0],reaction)
        for d in mt:
            print(d)
        print("")
        print("")
        #return MECAS

# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 22:25:22 2021

@author: Bjarne Gerdes
"""
import numpy as np

class CollectorLogik:   
    
    def __init__(self, rewards=[1,-1.5,2.5],
                sector_weights= [2,1,4,-1,-1],
                sensitivity_factor = 3,
                min_velocity = 2, min_action = 2):
        """
        Bei dieses Klasse handelt es sich um die Logik des regelbasierten Algorithmus.
        Demnach werden hier die Bilder erzeugt durch die Umgebung verarbeitet und daraus
        Steuersignale abgeleitet.

        Parameters
        ----------
        rewards : list, optional
            Beschreibungen, der Gewichtungsfaktoren der einzellnen Bälle, wobei die
            Liste wie folgt zu interpretieren ist:
            * rewards[0]: Belohnung für eine rote Kugel
            * rewards[1]: Belohnung für eine grüne Kugel
            * rewards[2]: Belohnung für eine blaue Kugel
            Dabei muss beachtet werden, dass diese Rewards nicht den tatsächlichen
            Punkten, die durch das Einsammeln der jeweiligen Farbe zu erzielen sind
            entsprechen müssen. In diesem Fall wurde der negative Reward für die grüne
            Kugel am stärksten angepasst, um zu verhindern, dass der Roboter zu 
            risikoavers reagiert.
                The default is [1,-1.5,2.5].
                
        sector_weights : list, optional
            Der Algorithmus unterteilt das Bild von links nach rechts
            in 5 Sektoren. Dabei wird für jeden Sektor der Score
            ermittelt. Dieser Score ergibt sich aus: 
                sqrt(Pixel des Sektors die einem Ball der jeweiligen Farbe zuzuordnen sind)
                * Reward für die jeweilige Farbe
                * Gewichtungsfaktor des jeweiligen Sektors (aus diesem Parameter)
                
            Aus den Faktoren resultierend ist, wie stark gewichtet wird,
            dass der Ball sich in dem jeweiligen Sektor befindet und
            daraus abgeleitet, wie wichtig es ist, dass der 
            Ball zentriert wird um sicherzustellen, dass er
            eingesammelt wird.
            Aus diesem Grund wird auch der Sektor, der der Mitte
            des Bildes darstellt, am stärksten Gewichtet.
                
            The default is [2,1,4,-1,-1].
            
        sensitivity_factor : int, optional
            Beeinflusst den Roboter, indem die aus den Scores 
            abgeleiteten Steuersignale durch den sensitivity_factor
            geteilt werden. Dies vermeidet zu hohe Velocity-Werte,
            die die maximal mögliche Eingabe von 6.28 überschreiten.
            The default is 3.
            
        min_velocity : TYPE, optional
            Beschreibt die minimale Velocity ab der der Roboter aufhört sich im Kreis zu drehen.
            Sorgt dafür, dass Bälle die weiter entfernt sind und somit einen niedrigeren Score
            haben, ignoriert werden.
            Demnach wird ein hohe Wert, dazu führen, dass der Algorithmus keine oder nur
            nahe Bälle berücksichtigen wird.
            -> Ist als heuristik eingeführt worden, um die Tatsache, dass die Zeit, die benötigt 
               wird zu einem Ball zu fahren in Relation zu dem Risiko steht, dass dieser
               Verschwindet
            The default is 2.
            
        min_action : TYPE, optional
            Funktioniert gleichermaßen wie min_velocity, wobei hier nicht die aggregierte
            Velocity betrachtet wird, sondern der action-Wert, für jeden einzellnen Sektor.
            Dies ist notwendig, da min_velocity nur die Entfernung der Bälle berücksichtigt
            und ergänzt wird durch diese Variable, die dazu führt, dass der Roboter
            sich dreht, wenn kein Ball sichtbar ist.            
            
            The default is 2.

        Returns
        -------
        None.

        """
        
        self.rewards = rewards
        self.velocity_left_long_term = []
        self.velocity_right_long_term = []
        self.sector_weights = sector_weights
        self.sensitivity_factor = sensitivity_factor
        self.min_velocity = min_velocity
        self.min_action = min_action
        
    def __get_score(self, image):
        """
        Als Eingabewert nimmt diese Funktion das Bild mit jeweils lediglich einem Farbwert.
        Anschließend wird das Bild in 5 Sektoren, von links nach rechts, unterteilt und jeweils
        die Anzahl der Pixel ermittelt die nach dem Filter verblieben sind.
        Üblicherweise funktioniert die Filterlogik sehr gut, wodurch dieser Wert als äquivalent 
        zu verstehen ist zum Kreisvolumen.
        
        Unter der Annahme, dass dieses Kreisvolumen sich exponentiell im Verhältnis zu der Distanz
        des Roboters zu diesem verhält, ist der Score entsprechend mit der Wurzel neutralisiert 
        worden, den Abstand zum Kreis linear zu halten 
        
        Parameters
        ----------
        image : np.array
            Farbwerte einer einzellnen Farbe pro
            Pixel im Bild.

        Returns
        -------
        np.array
            Numpy array mit den Scores pro Sektor.

        """
        # Bild in 5 verschiedene Sektoren aufteilen und anhand dessen für jeden dieser
        # Sektoren einen "Score" berechnen
        filtered_img = image.flatten()
        len_pixels = len(filtered_img)
        hard_left_score = sum(filtered_img[:int(len_pixels/5)] > 0)**.5
        soft_left_score = sum(filtered_img[int(len_pixels/5):int(len_pixels/5)*2] > 0 )**.5
        neutral_score = sum(filtered_img[int(len_pixels/5)*2:int(len_pixels/5)*3] > 0 )**.5
        soft_right_score = sum(filtered_img[int(len_pixels/5)*3:int(len_pixels/5)*4] > 0)**.5
        hard_right_score = sum(filtered_img[-int(len_pixels/5):] > 0)**.5
        
        return np.array([hard_left_score, soft_left_score, neutral_score, soft_right_score, hard_right_score])
         
     
    def __choose_action(self, image):
        """
        Berechnet den Score für jede Farbe und
        bestimmt und aggregiert diese unter
        berücksichtigung der Rewards


        Parameters
        ----------
        image : np.array
            Bild mit allen Farbräumen.

        Returns
        -------
        numpy.array
            Vektor mit Reward pro Sektor.

        """
        red_score = self.__get_score(image[:,:,0])
        green_score = self.__get_score(image[:,:,1])
        blue_score = self.__get_score(image[:,:,2])
        
     
        return (red_score*self.rewards[0] + green_score*self.rewards[1] + blue_score*self.rewards[2])
        
    
    def __ball_filter(self, image):
        """
        Umsetzen der Filterlogik, die dazu führt,
        dass lediglich jene Pixel erhalten beleiben,
        die zu einem Ball gehören.

        Parameters
        ----------
        image :
            Ausgabe der Funktion camera.getImageArray()
            des Roboters.

        Returns
        -------
        img_array : np.array
            Gefiltertes Bild als np.array.

        """
        img_array = np.array(image)
        
        # Lediglich die Farbwerte behalten, die doppelt so groß sind, wie die der beiden anderen Farben
        # Ist sehr gut in der Lage, die Bälle zu erkennen.
        filtered_red = (img_array[:,:,1]*2 < img_array[:,:,0]) & (img_array[:,:,2]*2 < img_array[:,:,0])
        filtered_green = (img_array[:,:,0]*2 < img_array[:,:,1]) & (img_array[:,:,2]*2 < img_array[:,:,1])
        filtered_blue = (img_array[:,:,0]*2 < img_array[:,:,2]) & (img_array[:,:,1]*2 < img_array[:,:,2])
    
    
        img_array[:,:,0][~filtered_red] = 0
        img_array[:,:,1][~filtered_green] = 0
        img_array[:,:,2][~filtered_blue] = 0
        
        return img_array


    def __action_to_velocity(self, action):
        """
        Unter Berücksichtung der Sektorgewichtungen und des 
        Sensitiviätsfaktors, werden die actions pro Sektor
        so aggregiert, dass aus diesen eine Velocity
        bestimmt wird.

        Gleichmaßen werden hier noch weitere regeln implementiert,
        die Verhindern, dass der Roboter zu sensitiv auf kleine 
        Änderungen reagiert und somit sichergestellt, dass er 
        sinnvoll auf seine Umgebung reagiert.
        
        Parameters
        ----------
        action : np.array
            Beschreibt die aus der Funktion __choose_action.
            Ermittelten Scores pro Sektor.

        Returns
        -------
        v_left : float
            Velocity des linken Rads.
        v_right : float
           Velocity des rechten Rads.

        """
        # Steuersignale definiere anhand der gegebenen Actionen
        velocity_right = np.sum(action*np.array(self.sector_weights))/self.sensitivity_factor
        velocity_left = np.sum(action*np.array(self.sector_weights[::-1]))/self.sensitivity_factor
         
        # Die "unsauberen" berechneten Steuersignale werden entsprechend gespeichert
        self.velocity_left_long_term.append(velocity_left)
        self.velocity_right_long_term.append(velocity_right)
     
        # Ableiten des velocity aus dem Mittel der "unsauberen" velocity-Werte
        # der letzen 5 Iterationen. Kann als Kurzzeitgedächtnis verstanden
        # werden und neutralisiert kleine Ausreißer in den Velocity-Werten.
        # Wert ist als 5 gewählt worden, da so zeitnah aber nicht instabil
        # reagiert wird. Ein höherer Wert, (bspw. 50) führt dazu, dass der
        # Roboter Schlangenlinien fährt.
        v_left = np.mean(self.velocity_left_long_term[-5:])
        v_right= np.mean(self.velocity_right_long_term[-5:])
        
        # Bestimmen, wie sinvoll es ist, zu fahren oder
        # weiter nach neuem Ball zu suchen
        if abs(v_left) <= self.min_velocity\
          and abs(v_right) <= self.min_velocity\
           or all(np.array(action) <= self.min_action):
            v_left = 6.28
            v_right = -6.28
            
        elif abs(v_left - v_right) < 1:
            v_left = 6.28
            v_right = 6.28
        
        # Skalieren der Werte auf das Intervall [-6.28, 6.28],
        # wenn nötig.
        elif abs(v_left) > 6.28 or abs(v_right) > 6.28:
            max_value = max([abs(v_left), abs(v_right)])
            multiplicator = 6.28/max_value
            v_left  *= multiplicator-0.0001 # avoid getting maxVelocity error with the 0.0001
            v_right  *= multiplicator-0.0001
        
        return v_left, v_right
        
    def choose(self, image):
        """
        Beschreibt die Zusammenarbeit aller der
        obigen Funktionen.

        Parameters
        ----------
        image :
            Ausgabe der Funktion camera.getImageArray()
            des Roboters.

        Returns
        -------
        v_left : float
            Velocity des linken Rads.
        v_right : float
           Velocity des rechten Rads.

        """
        img_filter = self.__ball_filter(image)
        action = self.__choose_action(img_filter)
        
        return self.__action_to_velocity(action)
 
from .extraterrestialUV import get_extraterrestial_UV
from pandas import DataFrame
from numpy import (
    arccos,
    arcsin,
    array,
    cos,
    sin,
    pi,
)


class CylinderRadiation:
    """
    Modelo Hay and Davis para la irradiancia solar sobre la superficie
    de un cilindro

    DOI: 10.1111/j.1751-1097.2009.00679.x
    """

    def __init__(
        self,
        params: dict,
        aspect: float,
        tilt: float,
    ) -> None:
        """
        Modelo Hay and Davis para la irradiancia solar sobre la superficie
        de un cilindro

        Entrada:
        ------------------------------------------------------------------
        params: diccionario con los nombres de las carpetas donde se encuentra
                la informacion

        aspect: grado entre 0 y 2pi, el cual hace referencia al giro del brazo
                sobre el plano XY
        tilt:   grado entre 0 y pi, el cual hace referencia al giro del brazo
                sobre el plano YZ
        """
        # Lectura de la irradiancia UV extraterrestre
        self.eed = get_extraterrestial_UV(
            params
        )
        # Guardado de los angulos
        self.aspect = aspect
        self.tilt = tilt
        # Definicion de las matrices de rotacion
        self._define_rotation_matrixes()
        # Inicializacion de las variables globales de la clase
        self.normal_vector_rotated = None
        self.incident_angle = None
        self.normal_vector = None
        self.eb = None

    def _to_radian(
        self,
        angle: float
    ) -> float:
        """
        Funcion para convertir a radianes un grado
        """
        return angle*pi/180

    def _to_degree(
        self,
        angle: float
    ) -> float:
        """
        Funcion para convertir de radianes a grados
        """
        return angle*180/pi

    def _define_rotation_matrixes(
        self,
    ) -> tuple:
        """
        Definicion de las matrices de rotacion

        r1 -> matriz que rota el brazo sobre el eje XY
        r2 -> matriz que rota al brazo sobre el eje XZ
        r3 -> matriz que rota al brazo sobre el eje XY
        """
        aspect_rad = self._to_radian(
            self.aspect
        )
        tilt_rad = self._to_radian(
            self.tilt
        )
        self.r1 = array([
            [
                cos(aspect_rad),
                -sin(aspect_rad),
                0,
            ],
            [
                sin(aspect_rad),
                cos(aspect_rad),
                0,
            ],
            [
                0,
                0,
                1
            ],
        ])
        self.r2 = array([
            [
                cos(tilt_rad),
                0,
                -sin(tilt_rad),
            ],
            [
                0,
                1,
                0,
            ],
            [
                sin(tilt_rad),
                0,
                cos(tilt_rad),
            ],
        ])
        self.r3 = array([
            [
                cos(-aspect_rad),
                -sin(-aspect_rad),
                0,
            ],
            [
                sin(-aspect_rad),
                cos(-aspect_rad),
                0,
            ],
            [
                0,
                0,
                1
            ],
        ])

    def estimate(
        self,
        sza: float,
        direct_beam: float,
        diffuse_beam: float,
        albedo: float,
    ) -> float:
        """
        Estimacion de la irradiancia solar sobre la superficie de un cilindro

        Entrada:
        ------------------------------------------------------------------
        sza: angulo zenital
        direct_beam: irradiancia solar directa
        diffuse_beam: irradiancia solar diffusa
        albedo: albedo de la superficie del brazo


        Salida:
        ------------------------------------------------------------------
        Irradiancia solar que recibe la superficie de un cilindro
        """
        results = DataFrame(
            index=range(-90, 90+5, 5),
            columns=["Ets"],
        )
        for slope in results.index:
            ets = self._estimate_per_slope(
                sza,
                slope,
                direct_beam,
                diffuse_beam,
                albedo,
            )
            results.loc[slope] = [ets]
        results = results.mean().iloc[0]
        return results

    def _estimate_per_slope(
        self,
        sza: float,
        slope: float,
        direct_beam: float,
        diffuse_beam: float,
        albedo: float,
    ) -> float:
        """
        Estimacion de la irradiancia solar sobre un segmento de la superficie
        de un cilindro

        Entrada:
        ------------------------------------------------------------------
        sza: angulo zenital
        slope: angulo caracterizado para el segmento del cilindro
        direct_beam: irradiancia solar directa
        diffuse_beam: irradiancia solar diffusa
        albedo: albedo de la superficie del brazo


        Salida:
        ------------------------------------------------------------------
        Irradiancia solar que recibe el segmento de la superficie del cilindro
        """
        # Irradiacion total
        total_beam = direct_beam+diffuse_beam
        # Definicion del vector normal al segmento
        self._define_normal_vector(
            slope,
        )
        # Rotacion del vector normal
        self._rotate_normal_vector()
        # Calculo del angulo incidente
        self._get_incident_angle(
            sza
        )
        # Rotacion de la pendiente del segmento
        slope = self._rotate_slope(
            slope,
        )
        # Calculo del primer termino de la funcion (parte directa)
        term1 = self._get_first_term(
            sza,
            direct_beam,
        )
        # Calculo del primer termino de la funcion (parte difusa)
        term2 = self._get_second_term(
            sza,
            slope,
            diffuse_beam,
        )
        # Calculo del primer termino de la funcion (parte total)
        term3 = self._get_third_term(
            slope,
            albedo,
            total_beam,
        )
        # Irradiacia solar sobre el segmento
        ets = term1+term2+term3
        return ets

    def _define_normal_vector(
        self,
        slope: float,
    ) -> array:
        """
        Definicion del vector normal a la superficie
        """
        aspect_rad = self._to_radian(
            self.aspect
        )
        slope_rad = self._to_radian(
            slope
        )
        self.normal_vector = array([
            -sin(aspect_rad)*sin(slope_rad),
            -cos(aspect_rad)*sin(slope_rad),
            cos(slope_rad)
        ])

    def _rotate_normal_vector(
        self
    ) -> array:
        """
        Rotacion del vector normal
        """
        matrix = self.r3@self.r2@self.r1
        self.normal_vector_rotated = matrix@self.normal_vector

    def _get_incident_angle(
        self,
        sza: float,
    ) -> float:
        """
        Calculo del angulo incidente sobre un segmento de la superficie del
        cilindro
        """
        sza_rad = self._to_radian(sza)
        _, n_y, n_z = self.normal_vector_rotated
        incident_angle = arccos(
            n_z*cos(sza_rad)-n_y*sin(sza_rad)
        )
        incident_angle = self._to_degree(
            incident_angle
        )
        self.incident_angle = 90-incident_angle

    def _rotate_slope(
        self,
        slope: float
    ) -> float:
        """
        Rotacion de la pendiente que caracteriza al segmento del cilindro
        """
        n_x, n_y, n_z = self.normal_vector
        aspect_rad = self._to_radian(
            self.aspect
        )
        tilt_rad = self._to_radian(
            self.tilt
        )
        term = n_x*cos(aspect_rad)-n_y*sin(aspect_rad)
        term *= sin(tilt_rad)
        term += n_z*cos(tilt_rad)
        slope = arcsin(term)
        slope = self._to_degree(
            slope
        )
        if 0 <= slope <= 180:
            slope = 90-slope
        if 180 < slope < 360:
            slope = 270+slope
        return slope

    def _get_eb(
        self,
        sza: float,
        direct_beam: float,
    ) -> float:
        """
        Calculo de la irradiancia solar directa horizontal
        """
        sza_rad = self._to_radian(sza)
        return direct_beam/cos(sza_rad)

    def _get_first_term(
        self,
        sza: float,
        direct_beam: float,
    ) -> float:
        """
        Calculo del primer termino de la ecuación de Hay and Davis
        """
        self.eb = self._get_eb(
            sza,
            direct_beam,
        )
        incident_angle_rad = self._to_radian(
            self.incident_angle
        )
        return self.eb*cos(incident_angle_rad)

    def _get_second_term(
        self,
        sza: float,
        slope: float,
        diffuse_beam: float,
    ) -> float:
        """
        Calculo del segundo termino de la ecuación de Hay and Davis
        """
        incident_angle_rad = self._to_radian(
            self.incident_angle
        )
        sza_rad = self._to_radian(
            sza
        )
        slope_rad = self._to_radian(
            slope
        )
        term1 = self.eb*cos(incident_angle_rad)
        term1 = term1/(self.eed*cos(sza_rad))
        term2 = 0.5*(1+cos(slope_rad))
        term3 = self.eb/self.eed
        term = term1+term2-term3
        term *= diffuse_beam
        return term

    def _get_third_term(
        self,
        slope: float,
        albedo: float,
        total_beam: float,
    ) -> float:
        """
        Calculo del tercer termino de la ecuación de Hay and Davis
        """
        slope_rad = self._to_radian(
            slope
        )
        term = 0.5*total_beam*albedo
        term *= (1-cos(slope_rad))
        return term

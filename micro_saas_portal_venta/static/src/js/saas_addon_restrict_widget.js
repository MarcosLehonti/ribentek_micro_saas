/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import "website_sale.website_sale"; // Importamos el widget original

publicWidget.registry.WebsiteSale.include({

    /**
     * Se ejecuta cuando la página del producto termina de cargar.
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        this._checkSaasSubscription();
        return def;
    },

    /**
     * Llamada RPC al servidor para verificar el estado de la suscripción SaaS
     */
    _checkSaasSubscription: function () {
        const $productForm = this.$el.closest('form'); // Formulario del producto

        // Verificamos si estamos en la página de TODO producto o si quieres puedes restringirlo 
        // revisando un data-attribute (ej: si el nombre/categoria tiene "SaaS")
        const isSaasProduct = this.$('.product_price').length > 0;

        if (!isSaasProduct) return;

        rpc('/shop/saas/check_subscription', {}).then((result) => {
            if (result.has_subscription) {
                this._applyRestrictiveAddonLogic(result, $productForm);
            }
        });
    },

    /**
     * Aplica la lógica de UI: Bloquea meses, asigna los restantes u otorga ventana de renovación.
     */
    _applyRestrictiveAddonLogic: function (data, $form) {
        // En Odoo normal, la cantidad está en input[name="add_qty"] o input.js_quantity
        const $qtyInput = $form.find('input[name="add_qty"]');
        const $addBtn = $form.find('.js_add_cart_json .fa-plus').closest('a');
        const $subBtn = $form.find('.js_add_cart_json .fa-minus').closest('a');

        if (data.is_renewal_window) {
            // Regla 4: Faltan < 15 días. Permitimos al usuario renovar libremente.
            $form.prepend(`
                <div class="alert alert-info mt-2">
                    <i class="fa fa-info-circle"></i> Tu suscripción expira en ${data.days_left} días. 
                    Puedes elegir un nuevo periodo de meses para tu renovación.
                </div>
            `);
            // El dropdown de atributos sigue normal por defecto nativo de Odoo.
            return;
        }

        // Regla 3.2: Tiene suscripción y NO está en ventana de renovación.
        if (data.remaining_months > 0) {
            // Forzamos el contador de cantidad a los meses restantes calculados por backend
            $qtyInput.val(data.remaining_months).trigger('change');

            // Bloqueamos la modificación de la cantidad (Meses)
            $qtyInput.prop('readonly', true);
            $addBtn.addClass('disabled').css('pointer-events', 'none');
            $subBtn.addClass('disabled').css('pointer-events', 'none');

            // Mensaje de Advertencia que wow al usuario explicando el co-termino
            $form.prepend(`
                <div class="alert alert-warning mt-2">
                    <i class="fa fa-lock"></i> Tienes la suscripción activa <b>${data.subscription_ref}</b>. 
                    <br/>Tus nuevos Add-ons (usuarios adicionales) serán alineados al vencimiento de tu plan actual (${data.remaining_months} meses restantes).
                </div>
            `);
        }
    }
});
